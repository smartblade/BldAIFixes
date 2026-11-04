#include <BWorld/OctTree.h>
#include <AnalyticGeometry/BoundingBox.h>
#include <BBLibc/BBLibc.h>
#include <BBLibc/MessageManager.h>
#include "bld_misc_funcs.h"


/*
* Module:                 Blade.exe
* Entry point:            0x00450327
* VC++ mangling:          ??0B_OctantNode@@QAE@XZ
*/

B_OctantNode::B_OctantNode()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450380
* VC++ mangling:          ??1B_OctantNode@@UAE@XZ
*/

B_OctantNode::~B_OctantNode()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450407
* VC++ mangling:          ?GetTypeID@B_OctantNode@@UAEHXZ
*/

int B_OctantNode::GetTypeID()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450417
* VC++ mangling:          ??0LeafNode@@QAE@XZ
*/

LeafNode::LeafNode()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450450
* VC++ mangling:          ??1LeafNode@@UAE@XZ
*/

LeafNode::~LeafNode()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045047C
* VC++ mangling:          ?GetTypeID@LeafNode@@UAEHXZ
*/

int LeafNode::GetTypeID()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045048C
* VC++ mangling:          ??0B_SectorListNode@@QAE@XZ
*/

B_SectorListNode::B_SectorListNode(): B_PtrArray<B_Sector>(1)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045050B
* VC++ mangling:          ??1B_SectorListNode@@UAE@XZ
*/

B_SectorListNode::~B_SectorListNode()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004506B5
* VC++ mangling:          ?GetTypeID@B_SectorListNode@@UAEHXZ
*/

int B_SectorListNode::GetTypeID()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004507B9
* VC++ mangling:          ??1B_OctTree@@QAE@XZ
*/

B_OctTree::~B_OctTree()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004507D5
* VC++ mangling:          ?Clear@B_OctTree@@QAEXXZ
*/

void B_OctTree::Clear()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450823
* VC++ mangling:          ?BuildNode@@YAPAVB_OctantNodeBase@@ABV?$B_PtrArray@VB_Sector@@@@NABVB_BoundingBox@@@Z
*/

// FIXME latest update broke this, need to investigate
B_OctantNodeBase* BuildNode(const B_PtrArray<B_Sector>& map, double sizeThreshold, const B_BoundingBox& worldBB)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00451A21
* VC++ mangling:          ?Build@B_OctTree@@QAEXABVB_Map@@N@Z
*/

void B_OctTree::Build(const B_Map& map, double minNodeSize)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045201F
* VC++ mangling:          ?CollectSectorsAtPoint@LeafNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void LeafNode::CollectSectorsAtPoint(const B_Vector& localPos, B_OctTreeSectorsList* outList, double halfSize)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452082
* VC++ mangling:          ?CollectSectorsInBox@LeafNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/

void LeafNode::CollectSectorsInBox(const B_BoundingBox&, B_OctTreeSectorsList* outList, double)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452191
* VC++ mangling:          ?CollectSectorsAtPoint@B_SectorListNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_SectorListNode::CollectSectorsAtPoint(const B_Vector& localPos, B_OctTreeSectorsList* outList, double halfSize)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452232
* VC++ mangling:          ?CollectSectorsInBox@B_SectorListNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_SectorListNode::CollectSectorsInBox(const B_BoundingBox&, B_OctTreeSectorsList* outList, double)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452388
* VC++ mangling:          ?CollectSectorsAtPoint@B_OctantNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_OctantNode::CollectSectorsAtPoint(
    const B_Vector& localPos, 
    B_OctTreeSectorsList* outList,
    double halfSize)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452845
* VC++ mangling:          ?CollectSectorsInBox@B_OctantNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_OctantNode::CollectSectorsInBox(const B_BoundingBox& bb, B_OctTreeSectorsList* outList, double halfSize)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00453067
* VC++ mangling:          ?FindSectorsAtPoint@B_OctTree@@UBEXABVB_Vector@@PAVB_OctTreeSectorsList@@@Z
*/

void B_OctTree::FindSectorsAtPoint(const B_Vector& worldPos, B_OctTreeSectorsList* outList) const
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045311A
* VC++ mangling:          ?FindSectorsInBox@B_OctTree@@UBEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@@Z
*/

void B_OctTree::FindSectorsInBox(const B_BoundingBox& bb, B_OctTreeSectorsList* out) const
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00453264
* VC++ mangling:          ??0B_OctTreeSectorsList@@QAE@XZ
*/

B_OctTreeSectorsList::B_OctTreeSectorsList() : size(0) {}
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045327B
* VC++ mangling:          ?BuildSurfaceCache@B_OctTreeSectorsList@@QAEHPAVB_GlobalSurfaceCache@@PBVB_Sphere@@@Z
*/

// TODO double check
int B_OctTreeSectorsList::BuildSurfaceCache(B_GlobalSurfaceCache* cache, const B_Sphere* sphere)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045346F
* VC++ mangling:          ??0B_SectorSurfaceCache@@QAE@XZ
*/

B_SectorSurfaceCache::B_SectorSurfaceCache()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00453490
* VC++ mangling:          ??1B_SectorSurfaceCache@@UAE@XZ
*/

B_SectorSurfaceCache::~B_SectorSurfaceCache()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004539A9
* VC++ mangling:          ??0B_GlobalSurfaceCache@@QAE@XZ
*/

B_GlobalSurfaceCache::B_GlobalSurfaceCache()
{
}

