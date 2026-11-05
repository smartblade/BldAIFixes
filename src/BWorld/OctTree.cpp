#include <BWorld/OctTree.h>
#include <AnalyticGeometry/BoundingBox.h>
#include <BBLibc/BBLibc.h>
#include <BBLibc/MessageManager.h>
#include <BBLibc/Vararg.h>
#include "bld_misc_funcs.h"
#include <math.h>


#define max(a,b) (((a) > (b)) ? (a) : (b))
#define min(a,b) (((a) < (b)) ? (a) : (b))


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x00450327
* VC++ mangling:          ??0B_OctantNode@@QAE@XZ
*/
B_OctantNode::B_OctantNode()
{
    for (unsigned int i = 0; i < 8; i++)
    {
        this->children[i] = nullptr;
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450380
* VC++ mangling:          ??1B_OctantNode@@UAE@XZ
*/
B_OctantNode::~B_OctantNode()
{
    for (unsigned int i = 0; i < 8; i++)
    {
        if (this->children[i] != nullptr)
        {
            delete this->children[i];
        }
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450407
* VC++ mangling:          ?GetTypeID@B_OctantNode@@UAEHXZ
*/

int B_OctantNode::GetTypeID() 
{
    return B_OCT_NODE_CID_BRANCH;
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450417
* VC++ mangling:          ??0LeafNode@@QAE@XZ
*/

LeafNode::LeafNode()
:
    sectors(nullptr)
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
    return B_OCT_NODE_CID_LEAF;
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045048C
* VC++ mangling:          ??0B_SectorListNode@@QAE@XZ
*/

B_SectorListNode::B_SectorListNode()
:
    B_PtrArray<B_Sector>(1)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045050B
* VC++ mangling:          ??1B_SectorListNode@@UAE@XZ
*/


B_SectorListNode::~B_SectorListNode()
{
    this->Clear(false);
}


/*
* Module:                 Blade.exe
* Entry point:            0x004506B5
* VC++ mangling:          ?GetTypeID@B_SectorListNode@@UAEHXZ
*/

int B_SectorListNode::GetTypeID()
{
    return B_OCT_NODE_CID_SECTOR_LIST;
}


/*
* Module:                 Blade.exe
* Entry point:            0x004506C5
* VC++ mangling:          ??0B_OctTree@@QAE@XZ
*/

B_OctTree::B_OctTree()
:
    m_halfSize(0.0),
    m_root(nullptr)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450734
* VC++ mangling:          ??0B_OctTree@@QAE@ABVB_Map@@N@Z
*/

B_OctTree::B_OctTree(const B_Map &map, double minNodeSize)
:
    m_halfSize(0.0),
    m_root(nullptr)
{
    this->Build(map, minNodeSize);
}


/*
* Module:                 Blade.exe
* Entry point:            0x004507B9
* VC++ mangling:          ??1B_OctTree@@QAE@XZ
*/

B_OctTree::~B_OctTree()
{
    this->Clear();
}


/*
* Module:                 Blade.exe
* Entry point:            0x004507D5
* VC++ mangling:          ?Clear@B_OctTree@@QAEXXZ
*/

void B_OctTree::Clear()
{
    if (this->m_root != nullptr)
    {
        delete this->m_root;
        this->m_root = nullptr;
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00450823
* VC++ mangling:          ?BuildNode@@YAPAVB_OctantNodeBase@@ABV?$B_PtrArray@VB_Sector@@@@NABVB_BoundingBox@@@Z
*/
B_OctantNodeBase *BuildNode(
    const B_PtrArray<B_Sector> &map,
    double sizeThreshold,
    const B_BoundingBox &worldBB
)
{
    if (map.size == 0)
        return nullptr;
    if (map.size == 1)
    {
        LeafNode *leaf = new LeafNode();
        leaf->sectors = map[0];
        return leaf;
    }
    if (
        worldBB.maxCoords.x - worldBB.minCoords.x < sizeThreshold ||
        map.size < 8
    )
    {
        B_SectorListNode *sectorList = new B_SectorListNode();
        for (unsigned int i = 0; i < map.size; i++)
            sectorList->Append(map[i]);
        return sectorList;
    }
    else
    {
        B_BoundingBox childBoundingBox;
        B_PtrArray<B_Sector> outBuffer;
        B_OctantNode *octantNode = new B_OctantNode();
        B_Vector boxCenter = (worldBB.minCoords + worldBB.maxCoords) * 0.5;
        childBoundingBox.minCoords = worldBB.minCoords;
        childBoundingBox.maxCoords = boxCenter;
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[0] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(worldBB.minCoords.x, worldBB.minCoords.y, boxCenter.z);
        childBoundingBox.maxCoords =
            B_Vector(boxCenter.x, boxCenter.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[1] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(worldBB.minCoords.x, boxCenter.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords =
            B_Vector(boxCenter.x, worldBB.maxCoords.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[2] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(worldBB.minCoords.x, boxCenter.y, boxCenter.z);
        childBoundingBox.maxCoords =
            B_Vector(boxCenter.x, worldBB.maxCoords.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[3] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(boxCenter.x, worldBB.minCoords.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords =
            B_Vector(worldBB.maxCoords.x, boxCenter.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[4] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(boxCenter.x, worldBB.minCoords.y, boxCenter.z);
        childBoundingBox.maxCoords =
            B_Vector(worldBB.maxCoords.x, boxCenter.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[5] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords =
            B_Vector(boxCenter.x, boxCenter.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords =
            B_Vector(worldBB.maxCoords.x, worldBB.maxCoords.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[6] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = boxCenter;
        childBoundingBox.maxCoords = worldBB.maxCoords;
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[7] =
            BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        return octantNode;
    }
}


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x00451A21
* VC++ mangling:          ?Build@B_OctTree@@QAEXABVB_Map@@N@Z
*/

void B_OctTree::Build(const B_Map &map, double minNodeSize)
{
    if (this->m_root != nullptr)
    {
        delete this->m_root;
    }
    this->m_halfSize = 0.0;
    B_BoundingBox worldBB;
    double max_x;
    double min_x;
    double max_y;
    double min_y;
    double max_z;
    double min_z;
    if (gbl_world_points.points.size != 0)
    {
        max_x = gbl_world_points.points[0].v.x;
        min_x = gbl_world_points.points[0].v.x;
        max_y = gbl_world_points.points[0].v.y;
        min_y = gbl_world_points.points[0].v.y;
        max_z = gbl_world_points.points[0].v.z;
        min_z = gbl_world_points.points[0].v.z;
        for (unsigned int i = 1; i < gbl_world_points.points.size; i++)
        {
            max_x = max(max_x, gbl_world_points.points[i].v.x);
            min_x = min(min_x, gbl_world_points.points[i].v.x);
            max_y = max(max_y, gbl_world_points.points[i].v.y);
            min_y = min(min_y, gbl_world_points.points[i].v.y);
            max_z = max(max_z, gbl_world_points.points[i].v.z);
            min_z = min(min_z, gbl_world_points.points[i].v.z);
        }
        this->m_halfSize =
            max(max_x - min_x, max(max_y - min_y, max_z - min_z)) +
                2.0 * minNodeSize;
        this->m_center.x = (max_x + min_x) * 0.5;
        this->m_center.y = (max_y + min_y) * 0.5;
        this->m_center.z = (max_z + min_z) * 0.5;
        worldBB.minCoords =
            this->m_center -
                0.5 *
                    B_Vector(
                        this->m_halfSize,
                        this->m_halfSize,
                        this->m_halfSize
                    );
        worldBB.maxCoords =
            this->m_center +
                0.5 *
                    B_Vector(
                        this->m_halfSize,
                        this->m_halfSize,
                        this->m_halfSize
                    );
    }
    this->m_root = BuildNode(map, minNodeSize, worldBB);
    mout << vararg("OctTree with %d nodes.\n", gbl_node_count);
}



/*
* Module:                 Blade.exe
* Entry point:            0x0045201F
* VC++ mangling:          ?CollectSectorsAtPoint@LeafNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void LeafNode::CollectSectorsAtPoint(
    const B_Vector &localPos,
    B_OctTreeSectorsList *outList,
    double halfSize
)
{
    if (
        this->sectors->lastQueryId != gbl_oct_tree_query_id &&
        this->sectors->isActive != 0
    )
    {
        this->sectors->lastQueryId = gbl_oct_tree_query_id;
        if (outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452082
* VC++ mangling:          ?CollectSectorsInBox@LeafNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/

void LeafNode::CollectSectorsInBox(
    const B_BoundingBox &, B_OctTreeSectorsList *outList,
    double
)
{
    if (
        this->sectors->lastQueryId != gbl_oct_tree_query_id &&
        this->sectors->isActive != 0
    )
    {
        this->sectors->lastQueryId = gbl_oct_tree_query_id;
        B_BoundingBox *sectorBB = &this->sectors->boundingBox;
        int intersects;
        if (
            gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x ||
            gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y ||
            gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z ||
            gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x ||
            gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y ||
            gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z
        )
        {
            intersects = 0;
        }
        else
        {
            intersects = 1;
        }
        if (intersects != 0 && outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452191
* VC++ mangling:          ?CollectSectorsAtPoint@B_SectorListNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_SectorListNode::CollectSectorsAtPoint(
    const B_Vector &localPos,
    B_OctTreeSectorsList *outList,
    double halfSize
)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (
            this->elements[i]->lastQueryId != gbl_oct_tree_query_id &&
            this->elements[i]->isActive != 0
        )
        {
            this->elements[i]->lastQueryId = gbl_oct_tree_query_id;
            if (outList->size < 512)
            {
                outList->sectors[outList->size] = this->elements[i];
                outList->size++;
            }
        }
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452232
* VC++ mangling:          ?CollectSectorsInBox@B_SectorListNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_SectorListNode::CollectSectorsInBox(
    const B_BoundingBox &, B_OctTreeSectorsList *outList,
    double
)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (
            this->elements[i]->lastQueryId != gbl_oct_tree_query_id &&
            this->elements[i]->isActive != 0
        )
        {
            this->elements[i]->lastQueryId = gbl_oct_tree_query_id;
            B_BoundingBox *sectorBB = &this->elements[i]->boundingBox;
            int intersects;
            if (
                gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x ||
                gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y ||
                gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z ||
                gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x ||
                gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y ||
                gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z
            )
            {
                intersects = 0;
            }
            else
            {
                intersects = 1;
            }
            if (intersects != 0 && outList->size < 512)
            {
                outList->sectors[outList->size] = this->elements[i];
                outList->size++;
            }
        }
    }
}




/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x00452388
* VC++ mangling:          ?CollectSectorsAtPoint@B_OctantNode@@UAEXABVB_Vector@@PAVB_OctTreeSectorsList@@N@Z
*/

void B_OctantNode::CollectSectorsAtPoint(
    const B_Vector &localPos,
    B_OctTreeSectorsList *outList,
    double halfSize
)
{
    double childHalfSize = halfSize / 2.0;
    double childCenterOffset = halfSize / 4.0;
    if (localPos.x < 10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[0] != nullptr)
            {
                this->children[0]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        -childCenterOffset,
                        -childCenterOffset,
                        -childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
            if (localPos.z > -10.0 && this->children[1] != nullptr)
            {
                this->children[1]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        -childCenterOffset,
                        -childCenterOffset,
                        childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[2] != nullptr)
            {
                this->children[2]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        -childCenterOffset,
                        childCenterOffset,
                        -childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
            if (localPos.z > -10.0 && this->children[3] != nullptr)
            {
                this->children[3]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        -childCenterOffset,
                        childCenterOffset,
                        childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
        }
    }
    if (localPos.x > -10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[4] != nullptr)
            {
                this->children[4]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        childCenterOffset,
                        -childCenterOffset,
                        -childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
            if (localPos.z > -10.0 && this->children[5] != nullptr)
            {
                this->children[5]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        childCenterOffset,
                        -childCenterOffset,
                        childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[6] != nullptr)
            {
                this->children[6]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        childCenterOffset,
                        childCenterOffset,
                        -childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
            if (localPos.z > -10.0 && this->children[7] != nullptr)
            {
                this->children[7]->CollectSectorsAtPoint(
                    localPos -
                    B_Vector(
                        childCenterOffset,
                        childCenterOffset,
                        childCenterOffset
                    ),
                        outList,
                        childHalfSize
                );
            }
        }
    }
}


/*
* Module:                 Blade.exe
* Entry point:            0x00452845
* VC++ mangling:          ?CollectSectorsInBox@B_OctantNode@@UAEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@N@Z
*/
void B_OctantNode::CollectSectorsInBox(
    const B_BoundingBox &bb,
    B_OctTreeSectorsList *outList,
    double halfSize
)
{
    double childHalfSize = halfSize / 2.0;
    double childCenterOffset = halfSize / 4.0;
    B_BoundingBox childBoundingBox = bb;
    if (bb.minCoords.x < 10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[0] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            -childCenterOffset,
                            -childCenterOffset,
                            -childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            -childCenterOffset,
                            -childCenterOffset,
                            -childCenterOffset
                        );
                this->children[0]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
            if (bb.maxCoords.z > -10.0 && this->children[1] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            -childCenterOffset,
                            -childCenterOffset,
                            childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            -childCenterOffset,
                            -childCenterOffset,
                            childCenterOffset
                        );
                this->children[1]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[2] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            -childCenterOffset,
                            childCenterOffset,
                            -childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            -childCenterOffset,
                            childCenterOffset,
                            -childCenterOffset
                        );
                this->children[2]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
            if (bb.maxCoords.z > -10.0 && this->children[3] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            -childCenterOffset,
                            childCenterOffset,
                            childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            -childCenterOffset,
                            childCenterOffset,
                            childCenterOffset
                        );
                this->children[3]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
        }
    }
    if (bb.maxCoords.x > -10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[4] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            childCenterOffset,
                            -childCenterOffset,
                            -childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            childCenterOffset,
                            -childCenterOffset,
                            -childCenterOffset
                        );
                this->children[4]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
            if (bb.maxCoords.z > -10.0 && this->children[5] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            childCenterOffset,
                            -childCenterOffset,
                            childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            childCenterOffset,
                            -childCenterOffset,
                            childCenterOffset
                        );
                this->children[5]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[6] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            childCenterOffset,
                            childCenterOffset,
                            -childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            childCenterOffset,
                            childCenterOffset,
                            -childCenterOffset
                        );
                this->children[6]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
            if (bb.maxCoords.z > -10.0 && this->children[7] != nullptr)
            {
                childBoundingBox.minCoords =
                    bb.minCoords -
                        B_Vector(
                            childCenterOffset,
                            childCenterOffset,
                            childCenterOffset
                        );
                childBoundingBox.maxCoords =
                    bb.maxCoords -
                        B_Vector(
                            childCenterOffset,
                            childCenterOffset,
                            childCenterOffset
                        );
                this->children[7]->CollectSectorsInBox(
                    childBoundingBox,
                    outList,
                    childHalfSize
                );
            }
        }
    }
}



/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x00453067
* VC++ mangling:          ?FindSectorsAtPoint@B_OctTree@@UBEXABVB_Vector@@PAVB_OctTreeSectorsList@@@Z
*/

void B_OctTree::FindSectorsAtPoint(
    const B_Vector &worldPos,
    B_OctTreeSectorsList *outList
) const
{
    outList->size = 0;
    B_Vector localPos = worldPos - this->m_center;
    gbl_oct_tree_query_id++;
    if (
        this->m_root != nullptr &&
        fabs(localPos.x) < this->m_halfSize + 10.0 &&
            fabs(localPos.y) < this->m_halfSize + 10.0 &&
                fabs(localPos.z) < this->m_halfSize + 10.0
    )
    {
        this->m_root->CollectSectorsAtPoint(
            localPos,
            outList,
            this->m_halfSize
        );
    }
}



/*
* Module:                 Blade.exe
* Entry point:            0x0045311A
* VC++ mangling:          ?FindSectorsInBox@B_OctTree@@UBEXABVB_BoundingBox@@PAVB_OctTreeSectorsList@@@Z
*/
void B_OctTree::FindSectorsInBox(
    const B_BoundingBox &bb,
    B_OctTreeSectorsList *out
) const
{
    out->size = 0;
    gbl_oct_tree_query_id++;
    gbl_current_query_box = &bb;
    B_BoundingBox localBB(
        bb.minCoords - this->m_center,
        bb.maxCoords - this->m_center
    );
    if (
        this->m_root != nullptr &&
        localBB.maxCoords.x > -this->m_halfSize * 0.5 - 10.0 &&
        localBB.maxCoords.y > -this->m_halfSize * 0.5 - 10.0 &&
        localBB.maxCoords.z > -this->m_halfSize * 0.5 - 10.0 &&
        localBB.minCoords.x < this->m_halfSize * 0.5 + 10.0 &&
        localBB.minCoords.y < this->m_halfSize * 0.5 + 10.0 &&
        localBB.minCoords.z < this->m_halfSize * 0.5 + 10.0
    )
    {
        this->m_root->CollectSectorsInBox(localBB, out, this->m_halfSize);
    }
}



/*
* Module:                 Blade.exe
* Entry point:            0x00453264
* VC++ mangling:          ??0B_OctTreeSectorsList@@QAE@XZ
*/
B_OctTreeSectorsList::B_OctTreeSectorsList()
:
    size(0)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0045327B
* VC++ mangling:          ?BuildSurfaceCache@B_OctTreeSectorsList@@QAEHPAVB_GlobalSurfaceCache@@PBVB_Sphere@@@Z
*/
int B_OctTreeSectorsList::BuildSurfaceCache(
    B_GlobalSurfaceCache *cache,
    const B_Sphere *sphere
)
{
    double distance;
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
            distance = current_surface->Distance(&sphere->center);
            if (-sphere->radius > distance)
            {
                j = current_sector->size + 1;
            }
            else if (distance < sphere->radius)
            {
                B_Surface *surface = current_sector->elements[j];
                cache->elements[cache->count].surfaces[cache->elements[cache->count].numSurfaces] =
                    surface;
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



/*
* Module:                 Blade.exe
* Entry point:            0x0045346F
* VC++ mangling:          ??0B_SectorSurfaceCache@@QAE@XZ
*/


B_SectorSurfaceCache::B_SectorSurfaceCache()
:
    numSurfaces(0)
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
* Entry point:            0x004534A4
* VC++ mangling:          ?IsPointInside@B_SectorSurfaceCache@@QAEHPBVB_Vector@@@Z
*/

int B_SectorSurfaceCache::IsPointInside(const B_Vector *point)
{
    for (unsigned int i = 0; i < this->numSurfaces; i++)
    {
        if (this->surfaces[i]->Distance(point) < 0.0)
        {
            return 0;
        }
    }
    return 1;
}


/*
* Module:                 Blade.exe
* Entry point:            0x004539A9
* VC++ mangling:          ??0B_GlobalSurfaceCache@@QAE@XZ
*/

B_GlobalSurfaceCache::B_GlobalSurfaceCache()
:
    count(0)
{
}



/*
................................................................................
................................................................................
................................................................................
................................................................................
*/



#ifndef BLD_NATIVE


#ifdef __cplusplus
extern "C" {
#endif

    unsigned int gbl_node_count;
    const B_BoundingBox *gbl_current_query_box;
    unsigned int gbl_oct_tree_query_id;


#ifdef __cplusplus
}
#endif

#endif
