# Review of BldMystery pull request 7

Pull request: [smartblade/BldMystery#7](https://github.com/smartblade/BldMystery/pull/7)
("Fix B_World class fields and offsets"), reviewed at commit `ee43e85`.

The procedures implemented in the pull request were converted by
BldRecompile (see `recompile/Blade.exe.cpp`). The issues below were found
while doing it. Each one comes with a suggested patch against `ee43e85` or
with suggested code. Sections 1-5 are bugs, sections 6-10 are differences of
the generated code from the original binary, section 11 is the code style
which makes the sources and the output of BldRecompile identical.

## 1. `~B_OctantNodeBase` is attributed to the scalar deleting destructor

`src/BWorld/OctTree.cpp` marks `0x00453AC0` as
`B_OctantNodeBase::~B_OctantNodeBase()` (`??1B_OctantNodeBase@@UAE@XZ`).
The code at this address is the compiler-generated scalar deleting
destructor of `B_OctantNodeBase`, not the destructor itself:

- it is the second entry of the `B_OctantNodeBase` vtable `g005BDD0C`,
  the slot of the virtual destructor;
- it takes the delete flag from `[ebp+8]`, calls `operator delete`
  (`l005BBD3D`) when bit 0 is set and returns with `ret 4`;
- the destructor body (`vtable = g005BDD0C; gbl_node_count--;`) is inlined
  into it, the destructor has no address of its own.

```asm
l00453AC0 PROC
           push ebp
           mov ebp, esp
           push ecx
           mov dword ptr [ebp-004h], ecx
           mov eax, dword ptr [ebp-004h]
           mov dword ptr [eax], offset g005BDD0C
           mov ecx, dword ptr [g005E338C]
           sub ecx, 000000001h
           mov dword ptr [g005E338C], ecx
           mov edx, dword ptr [ebp+008h]
           and edx, 000000001h
           test edx, edx
           je l00453AF5
           mov eax, dword ptr [ebp-004h]
           push eax
           call l005BBD3D
           add esp, 000000004h
l00453AF5: mov eax, dword ptr [ebp-004h]
           mov esp, ebp
           pop ebp
           ret 00004h
l00453AC0 ENDP
```

In the native build this is a bug: `procedures.inc` maps
`l00453AC0` to `??1B_OctantNodeBase@@UAE@XZ`, and the vtable still points
to `l00453AC0`. Deleting an octree node through a base class pointer
passes the delete flag, but the C++ destructor returns without popping it
(`ret` instead of `ret 4`) and never calls `operator delete`.

Suggested fix: remove the address from the destructor and regenerate
`native.asm`, so that the original code of `0x00453AC0` comes back.

```diff
--- a/src/BWorld/OctTree.cpp
+++ b/src/BWorld/OctTree.cpp
@@ -804,12 +804,6 @@ B_SectorSurfaceCache::~B_SectorSurfaceCache()
 */
 
 
-/*
-* Module:                 Blade.exe
-* Entry point:            0x00453AC0
-* VC++ mangling:          ??1B_OctantNodeBase@@UAE@XZ
-*/
-
 B_OctantNodeBase::~B_OctantNodeBase()
 {
     gbl_node_count--;
```

The constructor and the destructor of `B_OctantNodeBase` have no
addresses at all: their code (`vtable = g005BDD0C; gbl_node_count++;` and
`vtable = g005BDD0C; gbl_node_count--;`) is inlined into constructors and
destructors of `B_OctantNode`, `LeafNode` and `B_SectorListNode` and into
the scalar deleting destructor. With `/Ob1` Visual C++ inlines only inline
functions, so they are defined in the class in `OctTree.h`, not in
`OctTree.cpp`:

```cpp
class B_OctantNodeBase
{
public:
    B_OctantNodeBase()
    {
        gbl_node_count++;
    }

    virtual int GetTypeID() = 0;

    virtual ~B_OctantNodeBase()
    {
        gbl_node_count--;
    }
    ...
};
```

## 2. `B_BoundingBox::Intersects` returns `unsigned int`, not `bool`

`Intersects` (`0x0044F052`) is declared as returning `bool`, but it sets
the whole `eax` to 1 or 0, and its caller
`B_BoundingBox::CollectIntersectingSectors` tests the whole `eax`:

```asm
; end of B_BoundingBox::Intersects
           call l0044EDA9
           test eax, eax
           je l004501B7
           mov eax, 000000001h
           jmp l004501B9
l004501B7: xor eax, eax
l004501B9: pop edi
           pop esi
           mov esp, ebp
           pop ebp
           ret 00004h

; B_BoundingBox::CollectIntersectingSectors
           mov ecx, dword ptr [ebp-008h]
           push ecx
           mov ecx, dword ptr [ebp-024h]
           call l0044F052
           test eax, eax
           je l0045031B
```

A `bool` result would be returned and tested in `al` only. Suggested fix:
return `unsigned int` and update the mangled name (`_N` → `I`) in the
source and in `procedures.inc`.

```diff
--- a/src/AnalyticGeometry/BoundingBox.cpp
+++ b/src/AnalyticGeometry/BoundingBox.cpp
@@ -48,11 +48,11 @@ B_BoundingBox::B_BoundingBox(const B_Vector& minCoords, const B_Vector& maxCoord
 /*
 * Module:                 Blade.exe
 * Entry point:            0x0044F052
-* VC++ mangling:          ?Intersects@B_BoundingBox@@QBE_NPBVB_Sector@@@Z
+* VC++ mangling:          ?Intersects@B_BoundingBox@@QBEIPBVB_Sector@@@Z
 */
 
 #ifndef BLD_NATIVE
-bool B_BoundingBox::Intersects(const B_Sector* sector) const
+unsigned int B_BoundingBox::Intersects(const B_Sector* sector) const
 {
     return false;
 }
--- a/src/AnalyticGeometry/BoundingBox.h
+++ b/src/AnalyticGeometry/BoundingBox.h
@@ -24,7 +24,7 @@ public:
 
     void CollectIntersectingSectors(const B_PtrArray<B_Sector>&, B_PtrArray<B_Sector>&);
 
-    bool Intersects(const B_Sector* sector) const;
+    unsigned int Intersects(const B_Sector* sector) const;
 
     B_Vector minCoords;
     B_Vector maxCoords;
--- a/src/Blade/asm/procedures.inc
+++ b/src/Blade/asm/procedures.inc
@@ -660,8 +660,8 @@ externdef _GetMaterialFloatProperty: near
 l0044ED29 equ _GetMaterialFloatProperty
 externdef _AddHitSoundComb: near
 l0044ED6A equ _AddHitSoundComb
-externdef ?Intersects@B_BoundingBox@@QBE_NPBVB_Sector@@@Z: near
-l0044F052 equ ?Intersects@B_BoundingBox@@QBE_NPBVB_Sector@@@Z
+externdef ?Intersects@B_BoundingBox@@QBEIPBVB_Sector@@@Z: near
+l0044F052 equ ?Intersects@B_BoundingBox@@QBEIPBVB_Sector@@@Z
 externdef ?CollectIntersectingSectors@B_BoundingBox@@QAEXABV?$B_PtrArray@VB_Sector@@@@AAV2@@Z: near
 l004501C1 equ ?CollectIntersectingSectors@B_BoundingBox@@QAEXABV?$B_PtrArray@VB_Sector@@@@AAV2@@Z
 externdef ??0B_OctantNode@@QAE@XZ: near
```

## 3. Address of the `B_OctTreeSectorsList` constructor in `OctTree.h`

The address `0x00453264` of `B_OctTreeSectorsList::B_OctTreeSectorsList()`
is given twice: in `OctTree.cpp` above the definition and in `OctTree.h`
above the declaration inside the class. Address comments are expected
above definitions: the comment in the header is followed by a declaration
without a body, so the symbols collector takes everything up to the next
`{` (the rest of `B_OctTreeSectorsList` and the beginning of
`B_OctantNodeBase`) as the definition and assigns the constructor to
`B_OctantNodeBase`. Suggested fix: keep the address in `OctTree.cpp` only.

```diff
--- a/src/BWorld/OctTree.h
+++ b/src/BWorld/OctTree.h
@@ -41,11 +41,6 @@ public:
 class B_OctTreeSectorsList
 {
 public:
-    /*
-    * Module:                 Blade.exe
-    * Entry point:            0x00453264
-    * VC++ mangling:          ??0B_OctTreeSectorsList@@QAE@XZ
-    */
     B_OctTreeSectorsList();
 
     int BuildSurfaceCache(B_GlobalSurfaceCache* cache, const B_Sphere* sphere);
```

## 4. Typo in the mangling of `~B_Sector`

`src/BWorld/BMAP.CPP` has `VC++ man gling` instead of `VC++ mangling`
above `B_Sector::~B_Sector()` (`0x0042E26F`):

```cpp
/*
* Module:                 Blade.exe
* Entry point:            0x0042E26F
* VC++ man gling:          ??1B_Sector@@UAE@XZ
*/
```

Because of it the mangled name is not recognized and
`src/Blade/asm/procedures.inc` gets a name made from the procedure name
instead of `??1B_Sector@@UAE@XZ`:

```asm
externdef _B_Sector: near
l0042E26F equ _B_Sector
```

Suggested fix: correct the comment and regenerate `procedures.inc`.

```diff
--- a/src/BWorld/BMAP.CPP
+++ b/src/BWorld/BMAP.CPP
@@ -49,7 +49,7 @@
 /*
 * Module:                 Blade.exe
 * Entry point:            0x0042E26F
-* VC++ man gling:          ??1B_Sector@@UAE@XZ
+* VC++ mangling:          ??1B_Sector@@UAE@XZ
 */
 #ifndef BLD_NATIVE
 B_Sector::~B_Sector()
```

## 5. `B_OctTreeSectorsList::BuildSurfaceCache` does not match the binary

The `// TODO double check` above `BuildSurfaceCache` (`0x0045327B`) is
justified. The converted code (with names of local variables of the pull
request) is:

```cpp
int B_OctTreeSectorsList::BuildSurfaceCache(
    B_GlobalSurfaceCache *cache,
    const B_Sphere *sphere
)
{
    cache->count = 0;
    unsigned int i = 0;
    for (i = 0; i < this->size; i++)
    {
        B_Sector *current_sector = this->sectors[i];
        cache->elements[cache->count].sector = current_sector;
        cache->elements[cache->count].numSurfaces = 0;
        unsigned int j;
        for (j = 0; j < current_sector->size; j++)
        {
            B_Surface *current_surface = current_sector->elements[j];
            double distance =
                sphere->center.z * current_surface->normal.z +
                    sphere->center.y * current_surface->normal.y +
                    sphere->center.x * current_surface->normal.x +
                    current_surface->p;
            if (-sphere->radius > distance)
            {
                j = current_sector->size + 1;
            }
            else if (distance < sphere->radius)
            {
                B_Surface *unknown_loc_1C = current_sector->elements[j];
                cache->elements[cache->count].surfaces[cache->elements[cache->count].numSurfaces] =
                    unknown_loc_1C;
                cache->elements[cache->count].numSurfaces++;
            }
        }
        if (j == current_sector->size)
        {
            if (cache->elements[cache->count].numSurfaces == 0)
            {
                cache->elements[cache->count].hasNoIntersections = 1;
                cache->count++;
                return 1;
            }
            cache->elements[cache->count].hasNoIntersections = 0;
            cache->count++;
        }
    }
    if (cache->count != 0)
    {
        return 0;
    }
    return -1;
}
```

Differences from the pull request:

1. If `-sphere->radius > distance` (the sphere is outside one of the
   planes), the inner loop is aborted with `j = current_sector->size + 1`
   and the sector is **not** added to the cache: `cache->count` is not
   incremented. The pull request always adds the sector.
2. A surface is added if `distance < sphere->radius` (strict), the pull
   request uses `distance <= sphere->radius`.
3. If the inner loop finished (`j == current_sector->size`) and no surfaces
   were added, the function sets `hasNoIntersections = 1`, increments
   `cache->count` and **returns 1 immediately**. The pull request has no
   early return.
4. There is no `cacheEntry` local variable, the code accesses
   `cache->elements[cache->count]` every time. Loop counters are
   `unsigned int`.
5. The added surface is read from `current_sector->elements[j]` again into
   another local variable (`unknown_loc_1C`) instead of using
   `current_surface`.

The assembler code of `0x0045327B` confirms it.

Abort of the inner loop (difference 1):

```asm
           mov eax, dword ptr [ebp+00Ch]      ; sphere
           fld qword ptr [eax+018h]           ; ST0 = sphere->radius
           fchs                               ; ST0 = -radius
           fcomp qword ptr [ebp-008h]         ; compare with distance
           fnstsw ax
           test ah, 041h                      ; C0|C3: -radius <= distance
           jne l0045336C                      ; yes -> check the surface
           mov ecx, dword ptr [ebp-010h]      ; no (distance < -radius):
           mov edx, dword ptr [ecx+008h]      ;   current_sector->size
           add edx, 000000001h
           mov dword ptr [ebp-014h], edx      ;   j = current_sector->size + 1
           jmp l004533DD                      ;   j++ and exit the loop
```

Strict comparison with the radius (difference 2):

```asm
l0045336C: mov eax, dword ptr [ebp+00Ch]
           fld qword ptr [ebp-008h]           ; ST0 = distance
           fcomp qword ptr [eax+018h]         ; compare with radius
           fnstsw ax
           test ah, 001h                      ; C0: distance < radius
           je l004533DD                       ; no -> skip the surface
```

The sector is added only if the inner loop finished, and the function
returns 1 if no surfaces were added (difference 3):

```asm
l004533E2: mov eax, dword ptr [ebp-010h]
           mov ecx, dword ptr [ebp-014h]
           cmp ecx, dword ptr [eax+008h]      ; j == current_sector->size ?
           jne l00453455                      ; no (aborted) -> next sector, count is not incremented
           mov edx, dword ptr [ebp+008h]
           mov eax, dword ptr [edx]
           imul eax, eax, 000000110h
           mov ecx, dword ptr [ebp+008h]
           cmp dword ptr [ecx+eax+00Ch], 000000000h  ; numSurfaces == 0 ?
           jne l0045342F
           mov edx, dword ptr [ebp+008h]
           mov eax, dword ptr [edx]
           imul eax, eax, 000000110h
           mov ecx, dword ptr [ebp+008h]
           mov dword ptr [ecx+eax+000000110h], 000000001h  ; hasNoIntersections = 1
           mov edx, dword ptr [ebp+008h]
           mov eax, dword ptr [edx]
           add eax, 000000001h
           mov ecx, dword ptr [ebp+008h]
           mov dword ptr [ecx], eax           ; cache->count++
           mov eax, 000000001h
           jmp l00453469                      ; return 1
l0045342F: mov edx, dword ptr [ebp+008h]
           mov eax, dword ptr [edx]
           imul eax, eax, 000000110h
           mov ecx, dword ptr [ebp+008h]
           mov dword ptr [ecx+eax+000000110h], 000000000h  ; hasNoIntersections = 0
           mov edx, dword ptr [ebp+008h]
           mov eax, dword ptr [edx]
           add eax, 000000001h
           mov ecx, dword ptr [ebp+008h]
           mov dword ptr [ecx], eax           ; cache->count++
l00453455: jmp near ptr l0045329D             ; next sector
```

The rest matches the pull request: `cache->count = 0` at the start,
`distance` computed as z, y, x terms plus `p`, offsets in a cache element
of `0x110` (272) bytes (`sector` +4, `numSurfaces` +8, `surfaces` +12,
`hasNoIntersections` +268) and `return 0` / `return -1` at the end.

Suggested code:

```cpp
int B_OctTreeSectorsList::BuildSurfaceCache(B_GlobalSurfaceCache* cache, const B_Sphere* sphere)
{
    cache->count = 0;
    for (unsigned int i = 0; i < this->size; i++)
    {
        B_Sector* current_sector = this->sectors[i];
        cache->elements[cache->count].sector = current_sector;
        cache->elements[cache->count].numSurfaces = 0;
        unsigned int j;
        for (j = 0; j < current_sector->size; j++)
        {
            B_Surface* current_surface = current_sector->elements[j];
            double distance = (sphere->center.z * current_surface->normal.z) +
                (sphere->center.y * current_surface->normal.y) +
                (sphere->center.x * current_surface->normal.x) +
                current_surface->p;
            if (-sphere->radius > distance)
            {
                j = current_sector->size + 1;
            }
            else if (distance < sphere->radius)
            {
                B_SectorSurfaceCache& cacheEntry = cache->elements[cache->count];
                cacheEntry.surfaces[cacheEntry.numSurfaces] = current_surface;
                cacheEntry.numSurfaces++;
            }
        }
        if (j == current_sector->size)
        {
            if (cache->elements[cache->count].numSurfaces == 0)
            {
                cache->elements[cache->count].hasNoIntersections = 1;
                cache->count++;
                return 1;
            }
            cache->elements[cache->count].hasNoIntersections = 0;
            cache->count++;
        }
    }
    if (cache->count != 0)
    {
        return 0;
    }
    return -1;
}
```

## 6. `B_OctTree::~B_OctTree` calls a separate procedure

The destructor (`0x004507B9`) sets the vtable `g005BDD40` and calls a
separate, not inlined procedure `0x004507D5`, which deletes the root
(the pull request even has a `// 4507D5` comment):

```asm
l004507B9 PROC
           push ebp
           mov ebp, esp
           push ecx
           mov dword ptr [ebp-004h], ecx
           mov eax, dword ptr [ebp-004h]
           mov dword ptr [eax], offset g005BDD40
           mov ecx, dword ptr [ebp-004h]
           call l004507D5
           mov esp, ebp
           pop ebp
           ret
l004507B9 ENDP
l004507D5 PROC
           push ebp
           mov ebp, esp
           sub esp, 000000010h
           mov dword ptr [ebp-00Ch], ecx
           mov eax, dword ptr [ebp-00Ch]
           cmp dword ptr [eax+024h], 000000000h
           je l0045081F
           ...
           push 000000001h
           mov ecx, dword ptr [ebp-004h]
           mov edx, dword ptr [ecx]
           mov ecx, dword ptr [ebp-004h]
           call [edx+004h]
           ...
l00450815: mov eax, dword ptr [ebp-00Ch]
           mov dword ptr [eax+024h], 000000000h
l0045081F: mov esp, ebp
           pop ebp
           ret
l004507D5 ENDP
```

The pull request inlines the body of `0x004507D5` into the destructor.
Suggested fix: move it into a separate method (for example `Clear()`) with
the address `0x004507D5` and call it from the destructor:

```cpp
B_OctTree::~B_OctTree()
{
    Clear();
}

void B_OctTree::Clear()
{
    if (this->m_root != nullptr) {
        delete this->m_root;
        this->m_root = nullptr;
    }
}
```

## 7. Members initialized in constructor bodies instead of initializer lists

In these constructors the binary writes the member before setting the
vtable (or, for `B_GlobalSurfaceCache`, before constructing `elements`),
so the member is initialized in the initializer list:

| Address | Constructor | Suggested |
|---|---|---|
| `0x00450417` | `LeafNode::LeafNode()` | `: sectors(nullptr)` |
| `0x0045346F` | `B_SectorSurfaceCache::B_SectorSurfaceCache()` | `: numSurfaces(0)` |
| `0x004539A9` | `B_GlobalSurfaceCache::B_GlobalSurfaceCache()` | `: count(0)` |

```asm
l00450417 PROC                              ; LeafNode::LeafNode()
           ...
           mov dword ptr [eax], offset g005BDD0C  ; B_OctantNodeBase vtable
           mov ecx, dword ptr [g005E338C]
           add ecx, 000000001h
           mov dword ptr [g005E338C], ecx         ; gbl_node_count++
           mov edx, dword ptr [ebp-004h]
           mov dword ptr [edx+004h], 000000000h   ; sectors = nullptr
           mov eax, dword ptr [ebp-004h]
           mov dword ptr [eax], offset g005BDD1C  ; LeafNode vtable
           ...
l0045346F PROC                              ; B_SectorSurfaceCache::B_SectorSurfaceCache()
           ...
           mov dword ptr [eax+008h], 000000000h   ; numSurfaces = 0
           mov ecx, dword ptr [ebp-004h]
           mov dword ptr [ecx], offset g005BDD50  ; B_SectorSurfaceCache vtable
           ...
```

`B_GlobalSurfaceCache::B_GlobalSurfaceCache()` sets `count` to 0 before
constructing 128 `elements`:

```cpp
B_GlobalSurfaceCache::B_GlobalSurfaceCache()
{
    this->count = 0;
    int unknown_loc_0C = 128;
    STACKVAR(-8, 4) = 0x00000110;
    STACKVAR(-4, 4) = &this->elements;
l004539D2:
    unknown_loc_0C--;
    if (unknown_loc_0C >= 0)
    {
        reinterpret_cast<B_SectorSurfaceCache *>(STACKVAR(-4, 4))->B_SectorSurfaceCache();
        ...
    }
}
```

## 8. `B_SectorListNode::CollectSectorsInBox` differs from `LeafNode::CollectSectorsInBox`

`B_SectorListNode::CollectSectorsInBox` (`0x00452232`) gives the same
result as in the pull request, but it is compiled the same way as
`LeafNode::CollectSectorsInBox` (`0x00452082`): there is no `queryBB`
local variable (`gbl_current_query_box` is read every time), the
intersection flag is computed with strict `>`/`<` comparisons and then
tested:

```cpp
void B_SectorListNode::CollectSectorsInBox(
    const B_BoundingBox &bb,
    B_OctTreeSectorsList *outList,
    double halfSize
)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (
            this->elements[i]->lastQueryId !=
            static_cast<int>(gbl_oct_tree_query_id) &&
                this->elements[i]->isActive != 0
        )
        {
            this->elements[i]->lastQueryId =
                static_cast<int>(gbl_oct_tree_query_id);
            B_BoundingBox *sectorBB = &this->elements[i]->boundingBox;
            if (
                !(
                    gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x ||
                    gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y ||
                    gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z ||
                    gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x ||
                    gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y ||
                    gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z
                ) &&
                outList->size < 512
            )
            {
                outList->sectors[outList->size] = this->elements[i];
                outList->size++;
            }
        }
    }
}
```

Both procedures keep the flag in a local variable (`[ebp-008h]`) before
testing it. The `<=`/`>=` comparisons of the pull request are not the same
as negated `>`/`<` comparisons for NaN coordinates.

Suggested fix: write it like `LeafNode::CollectSectorsInBox`, with a
`B_BoundingBox* sectorBB = &(*this)[i]->boundingBox;` local and an
`intersects` flag.

## 9. Minor differences

- `B_Sector::lastQueryId` is declared as `int`, but `gbl_oct_tree_query_id`
  is `unsigned int`, so `LeafNode::CollectSectorsAtPoint` and
  `LeafNode::CollectSectorsInBox` compare signed and unsigned values. In
  `B_SectorListNode` the same field is compared as `unsigned int`. It is
  probably `unsigned int`.
- In `B_BoundingBox::CollectIntersectingSectors` the element passed to the
  inlined `Append` is read from `sectors.elements[i]` again instead of
  using the `sector` local variable:

  ```cpp
  B_Sector *unknown_loc_08 = reinterpret_cast<B_Sector *>(ACCESS(ARRPTR(sectors.elements, 4, unknown_loc_04, 0), 0, 4));
  if (this->Intersects(unknown_loc_08) == 0)
  {
      goto l0045031B;
  }
  STACKVAR(-12, 4) = ACCESS(ARRPTR(sectors.elements, 4, unknown_loc_04, 0), 0, 4);
  ```

  The original code was probably `outBuffer.Append(sectors.elements[i])`
  (or `sectors[i]`), but this is a guess.

- Parameters of `LeafNode::CollectSectorsInBox` and
  `B_SectorListNode::CollectSectorsInBox` have no names:
  `(const B_BoundingBox&, B_OctTreeSectorsList* outList, double)`. Names of
  the base class declaration are suggested: `bb` and `halfSize`.

## 10. Octree constants are literals, not `static double` variables

`src/BWorld/OctTree.cpp` declares

```cpp
static double child_size_divisor = 2.0;
static double child_offset_divisor = 4.0;
static double kOctTreeMargin = 10.0;
```

and compares coordinates with `kOctTreeMargin` and `-kOctTreeMargin`. In
the binary the values are read from `.rdata` (`005BD000`-`005C7072`),
which is not writable, while non-const `static double` variables would be
placed to `.data` (`005C8000`). `-kOctTreeMargin` is not computed with
`fchs` either, it is a separate constant `-10.0`:

| Address | Value |
|---|---|
| `0x005BD710` | `2.0` |
| `0x005BDB68` | `4.0` |
| `0x005BDB88` | `10.0` |
| `0x005BDD48` | `-10.0` |

```asm
l00452388 PROC                          ; B_OctantNode::CollectSectorsAtPoint
           ...
           fld qword ptr [ebp+010h]     ; halfSize
           fdiv qword ptr [g005BD710]   ; / 2.0
           fstp qword ptr [ebp-008h]
           fld qword ptr [ebp+010h]     ; halfSize
           fdiv qword ptr [g005BDB68]   ; / 4.0
           fstp qword ptr [ebp-010h]
           ...
           fld qword ptr [eax]          ; localPos.x
           fcomp qword ptr [g005BDB88]  ; < 10.0
           ...
           fcomp qword ptr [g005BDD48]  ; > -10.0
```

The converted code (`B_OctantNode::CollectSectorsAtPoint`,
`B_OctantNode::CollectSectorsInBox`, `B_OctTree::FindSectorsAtPoint`):

```cpp
STACKVAR(-8, 8) = halfSize / 2.0;
STACKVAR(-16, 8) = halfSize / 4.0;
if (localPos.x < 10.0)
...
            if (localPos.z > -10.0 && ACCESS(this, 8, 4) != 0x00000000)
...
if (this->m_root != nullptr && this->m_halfSize + 10.0 > fabs(reinterpret_cast<double>(STACKVAR(-24, 8))) && ...)
```

So the original code used literals (`2.0`, `4.0`, `10.0`, `-10.0`) or
`const double` constants, which the compiler replaces with literals. With
the `static double` variables of the pull request the compiler reads them
from `.data` and computes `-kOctTreeMargin` with `fld` and `fchs`.
Suggested fix: use literals or `const double` constants.

## 11. Code style

The goal is that the implemented procedures are identical to the output of
BldRecompile. The compiler doesn't keep the differences below, so the style
of BldRecompile output is used:

1. `&` and `*` are attached to names, not to types:
   `const B_Vector &that`, `B_Sector *sector`.
2. Opening braces are on separate lines, there is no `;` after the closing
   brace of a function:

   ```cpp
   int B_SectorListNode::GetTypeID()
   {
       return B_OCT_NODE_CID_SECTOR_LIST;
   }
   ```

3. Loop counters are incremented with postfix `i++`, not `++i`.
4. Fields and methods are accessed with explicit `this->`:
   `this->children[i] = nullptr;`.
5. Nested `if` statements without `else` are merged with `&&`:
   `if (bb.minCoords.z < 10.0 && this->children[0] != nullptr)` instead of
   `if (bb.minCoords.z < 10.0) { if (children[0]) { ... } }`.
6. Integer literals are decimal: `outList->size < 512`, not `0x200`.
7. There are no comments and no commented out code inside procedures,
   e.g. `// mark as "processed"`, `// TODO double check` and the commented
   out implementation of `B_Vector::operator -`.
8. Lines longer than 80 characters are wrapped the way BldRecompile does
   it when it updates sources (`process_asm.py --update-src-at`):

   ```cpp
   void LeafNode::CollectSectorsInBox(
       const B_BoundingBox &bb,
       B_OctTreeSectorsList *outList,
       double halfSize
   )
   {
       ...
           if (
               !(
                   gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x ||
                   gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y ||
                   gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z ||
                   gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x ||
                   gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y ||
                   gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z
               ) &&
               outList->size < 512
           )
   ```

9. Procedures of a source file are in the order of their addresses: Visual
   C++ 6 places procedures of a file in the order of their definitions. In
   `OctTree.cpp` `B_SectorSurfaceCache::~B_SectorSurfaceCache` (0x00453490)
   must be defined before `B_GlobalSurfaceCache::B_GlobalSurfaceCache`
   (0x004539A9). BldRecompile can't update sources with procedures in other
   order.
10. There are no blank lines inside procedures, including empty bodies and
    lines before `return`:

    ```cpp
    B_SectorListNode::~B_SectorListNode()
    {
    }

    int B_OctantNode::GetTypeID()
    {
        return B_OCT_NODE_CID_BRANCH;
    }
    ```

## Procedures that match the binary

`B_Sphere::B_Sphere`, `B_BoundingBox::B_BoundingBox(min, max)`,
`B_Vector::operator -`, `B_BoundingBox::CollectIntersectingSectors` (apart
from section 9), `B_OctantNode::B_OctantNode`, `B_OctantNode::~B_OctantNode`,
all `GetTypeID` methods, `LeafNode::~LeafNode`,
`B_SectorListNode::B_SectorListNode`, `B_SectorListNode::~B_SectorListNode`,
`LeafNode::CollectSectorsAtPoint`, `LeafNode::CollectSectorsInBox`,
`B_SectorListNode::CollectSectorsAtPoint`,
`B_OctantNode::CollectSectorsAtPoint`, `B_OctantNode::CollectSectorsInBox`
(conditions, offset signs, children indices, vtable slots and constants
2.0, 4.0, 10.0 and -10.0 of all 8 children), `B_OctTree::FindSectorsAtPoint`,
`B_OctTreeSectorsList::B_OctTreeSectorsList` and
`B_SectorSurfaceCache::~B_SectorSurfaceCache`.
