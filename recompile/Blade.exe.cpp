
// address: 0x00401000
B_Sphere::B_Sphere()
:
    radius(0.0)
{
}

// address: 0x00401548
B_BoundingBox::B_BoundingBox()
{
}

// address: 0x004015C5
B_BoundingBox::B_BoundingBox(const B_Vector &minCoords, const B_Vector &maxCoords)
:
    minCoords(minCoords),
    maxCoords(maxCoords)
{
}

// address: 0x0040A5D0
B_Vector B_Vector::operator -(const B_Vector &that) const
{
    return B_Vector(this->x - that.x, this->y - that.y, this->z - that.z);
}

// address: 0x004501C1
void B_BoundingBox::CollectIntersectingSectors(const B_PtrArray<B_Sector> &sectors, B_PtrArray<B_Sector> &outBuffer)
{
    for (unsigned int i = 0; i < sectors.size; i++)
    {
        B_Sector *sector = sectors.elements[i];
        if (this->Intersects(sector))
        {
            B_Sector *newElement = sectors.elements[i];
            outBuffer.Append(newElement);
        }
    }
}

// address: 0x00450327
B_OctantNode::B_OctantNode()
{
    for (unsigned int i = 0; i < 8; i++)
    {
        this->children[i] = nullptr;
    }
}

// address: 0x00450380
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

// address: 0x00450407
int B_OctantNode::GetTypeID()
{
    return B_OCT_NODE_CID_BRANCH;
}

// address: 0x00450417
LeafNode::LeafNode()
:
    sectors(nullptr)
{
}

// address: 0x00450450
LeafNode::~LeafNode()
{
}

// address: 0x0045047C
int LeafNode::GetTypeID()
{
    return B_OCT_NODE_CID_LEAF;
}

// address: 0x0045048C
B_SectorListNode::B_SectorListNode()
:
    B_PtrArray<B_Sector>(1)
{
}

// address: 0x0045050B
B_SectorListNode::~B_SectorListNode()
{
    this->Clear(false);
}

// address: 0x004506B5
int B_SectorListNode::GetTypeID()
{
    return B_OCT_NODE_CID_SECTOR_LIST;
}

// address: 0x004506C5
B_OctTree::B_OctTree()
:
    m_halfSize(0.0),
    m_root(nullptr)
{
}

// address: 0x004507B9
B_OctTree::~B_OctTree()
{
    this->Clear();
}

// address: 0x004507D5
void B_OctTree::Clear()
{
    if (this->m_root != nullptr)
    {
        delete this->m_root;
        this->m_root = nullptr;
    }
}

// address: 0x00450823
B_OctantNodeBase *BuildNode(const B_PtrArray<B_Sector> &map, double sizeThreshold, const B_BoundingBox &worldBB)
{
    if (map.size == 0)
    {
        return nullptr;
    }
    if (map.size == 1)
    {
        LeafNode *leaf = new LeafNode();
        leaf->sectors = map[0];
        return leaf;
    }
    if (worldBB.maxCoords.x - worldBB.minCoords.x < sizeThreshold || map.size < 8)
    {
        B_SectorListNode *sectorList = new B_SectorListNode();
        for (unsigned int i = 0; i < map.size; i++)
        {
            sectorList->Append(map[i]);
        }
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
        octantNode->children[0] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(worldBB.minCoords.x, worldBB.minCoords.y, boxCenter.z);
        childBoundingBox.maxCoords = B_Vector(boxCenter.x, boxCenter.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[1] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(worldBB.minCoords.x, boxCenter.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords = B_Vector(boxCenter.x, worldBB.maxCoords.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[2] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(worldBB.minCoords.x, boxCenter.y, boxCenter.z);
        childBoundingBox.maxCoords = B_Vector(boxCenter.x, worldBB.maxCoords.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[3] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(boxCenter.x, worldBB.minCoords.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords = B_Vector(worldBB.maxCoords.x, boxCenter.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[4] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(boxCenter.x, worldBB.minCoords.y, boxCenter.z);
        childBoundingBox.maxCoords = B_Vector(worldBB.maxCoords.x, boxCenter.y, worldBB.maxCoords.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[5] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = B_Vector(boxCenter.x, boxCenter.y, worldBB.minCoords.z);
        childBoundingBox.maxCoords = B_Vector(worldBB.maxCoords.x, worldBB.maxCoords.y, boxCenter.z);
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[6] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        childBoundingBox.minCoords = boxCenter;
        childBoundingBox.maxCoords = worldBB.maxCoords;
        childBoundingBox.CollectIntersectingSectors(map, outBuffer);
        octantNode->children[7] = BuildNode(outBuffer, sizeThreshold, childBoundingBox);
        outBuffer.Clear(false);
        return octantNode;
    }
}

// address: 0x00451A21
void B_OctTree::Build(const B_Map &map, double minNodeSize)
{
    if (this->m_root != nullptr)
    {
        delete this->m_root;
    }
    this->m_halfSize = 0.0;
    B_BoundingBox unknown_loc_50;
    if (gbl_world_points.points.size == 0)
    {
        goto l00451FD1;
    }
    double unknown_loc_10;
    unknown_loc_10 = gbl_world_points.points[0].v.x;
    double unknown_loc_58;
    unknown_loc_58 = gbl_world_points.points[0].v.x;
    double unknown_loc_18;
    unknown_loc_18 = gbl_world_points.points[0].v.y;
    double unknown_loc_60;
    unknown_loc_60 = gbl_world_points.points[0].v.y;
    double unknown_loc_20;
    unknown_loc_20 = gbl_world_points.points[0].v.z;
    double unknown_loc_08;
    unknown_loc_08 = gbl_world_points.points[0].v.z;
    for (unsigned int unknown_loc_64 = 1; unknown_loc_64 < gbl_world_points.points.size; unknown_loc_64++)
    {
        unknown_loc_10 = max(unknown_loc_10, gbl_world_points.points[unknown_loc_64].v.x);
        unknown_loc_58 = min(unknown_loc_58, gbl_world_points.points[unknown_loc_64].v.x);
        unknown_loc_18 = max(unknown_loc_18, gbl_world_points.points[unknown_loc_64].v.y);
        unknown_loc_60 = min(unknown_loc_60, gbl_world_points.points[unknown_loc_64].v.y);
        unknown_loc_20 = max(unknown_loc_20, gbl_world_points.points[unknown_loc_64].v.z);
        unknown_loc_08 = min(unknown_loc_08, gbl_world_points.points[unknown_loc_64].v.z);
    }
    this->m_halfSize = max(unknown_loc_10 - unknown_loc_58, max(unknown_loc_18 - unknown_loc_60, unknown_loc_20 - unknown_loc_08)) + 2.0 * minNodeSize;
    this->m_center.x = (unknown_loc_10 + unknown_loc_58) * 0.5;
    this->m_center.y = (unknown_loc_18 + unknown_loc_60) * 0.5;
    this->m_center.z = (unknown_loc_20 + unknown_loc_08) * 0.5;
    unknown_loc_50.minCoords = this->m_center - 0.5 * B_Vector(this->m_halfSize, this->m_halfSize, this->m_halfSize);
    unknown_loc_50.maxCoords = this->m_center + 0.5 * B_Vector(this->m_halfSize, this->m_halfSize, this->m_halfSize);
l00451FD1:
    this->m_root = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(&map), minNodeSize, unknown_loc_50);
    ??6@YAAAVB_MessageManager@@AAV0@PBD@Z(&?mout@@3VB_MessageManager@@A, ?vararg@@YAPBDPBDZZ(GLOBAL(0x005CFE3C), gbl_node_count));
}

// address: 0x0045201F
void LeafNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    if (this->sectors->lastQueryId != gbl_oct_tree_query_id && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = gbl_oct_tree_query_id;
        if (outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}

// address: 0x00452082
void LeafNode::CollectSectorsInBox(const B_BoundingBox &, B_OctTreeSectorsList *outList, double)
{
    if (this->sectors->lastQueryId != gbl_oct_tree_query_id && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = gbl_oct_tree_query_id;
        B_BoundingBox *sectorBB = &this->sectors->boundingBox;
        int intersects;
        if (gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x || gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y || gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z || gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x || gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y || gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z)
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

// address: 0x00452191
void B_SectorListNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (this->elements[i]->lastQueryId != gbl_oct_tree_query_id && this->elements[i]->isActive != 0)
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

// address: 0x00452232
void B_SectorListNode::CollectSectorsInBox(const B_BoundingBox &, B_OctTreeSectorsList *outList, double)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (this->elements[i]->lastQueryId != gbl_oct_tree_query_id && this->elements[i]->isActive != 0)
        {
            this->elements[i]->lastQueryId = gbl_oct_tree_query_id;
            B_BoundingBox *sectorBB = &this->elements[i]->boundingBox;
            int intersects;
            if (gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x || gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y || gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z || gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x || gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y || gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z)
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

// address: 0x00452388
void B_OctantNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    double childHalfSize = halfSize / 2.0;
    double childCenterOffset = halfSize / 4.0;
    if (localPos.x < 10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[0] != nullptr)
            {
                this->children[0]->CollectSectorsAtPoint(localPos - B_Vector(-childCenterOffset, -childCenterOffset, -childCenterOffset), outList, childHalfSize);
            }
            if (localPos.z > -10.0 && this->children[1] != nullptr)
            {
                this->children[1]->CollectSectorsAtPoint(localPos - B_Vector(-childCenterOffset, -childCenterOffset, childCenterOffset), outList, childHalfSize);
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[2] != nullptr)
            {
                this->children[2]->CollectSectorsAtPoint(localPos - B_Vector(-childCenterOffset, childCenterOffset, -childCenterOffset), outList, childHalfSize);
            }
            if (localPos.z > -10.0 && this->children[3] != nullptr)
            {
                this->children[3]->CollectSectorsAtPoint(localPos - B_Vector(-childCenterOffset, childCenterOffset, childCenterOffset), outList, childHalfSize);
            }
        }
    }
    if (localPos.x > -10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[4] != nullptr)
            {
                this->children[4]->CollectSectorsAtPoint(localPos - B_Vector(childCenterOffset, -childCenterOffset, -childCenterOffset), outList, childHalfSize);
            }
            if (localPos.z > -10.0 && this->children[5] != nullptr)
            {
                this->children[5]->CollectSectorsAtPoint(localPos - B_Vector(childCenterOffset, -childCenterOffset, childCenterOffset), outList, childHalfSize);
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[6] != nullptr)
            {
                this->children[6]->CollectSectorsAtPoint(localPos - B_Vector(childCenterOffset, childCenterOffset, -childCenterOffset), outList, childHalfSize);
            }
            if (localPos.z > -10.0 && this->children[7] != nullptr)
            {
                this->children[7]->CollectSectorsAtPoint(localPos - B_Vector(childCenterOffset, childCenterOffset, childCenterOffset), outList, childHalfSize);
            }
        }
    }
}

// address: 0x00452845
void B_OctantNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
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
                childBoundingBox.minCoords = bb.minCoords - B_Vector(-childCenterOffset, -childCenterOffset, -childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(-childCenterOffset, -childCenterOffset, -childCenterOffset);
                this->children[0]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -10.0 && this->children[1] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(-childCenterOffset, -childCenterOffset, childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(-childCenterOffset, -childCenterOffset, childCenterOffset);
                this->children[1]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[2] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(-childCenterOffset, childCenterOffset, -childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(-childCenterOffset, childCenterOffset, -childCenterOffset);
                this->children[2]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -10.0 && this->children[3] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(-childCenterOffset, childCenterOffset, childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(-childCenterOffset, childCenterOffset, childCenterOffset);
                this->children[3]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
        }
    }
    if (bb.maxCoords.x > -10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[4] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(childCenterOffset, -childCenterOffset, -childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(childCenterOffset, -childCenterOffset, -childCenterOffset);
                this->children[4]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -10.0 && this->children[5] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(childCenterOffset, -childCenterOffset, childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(childCenterOffset, -childCenterOffset, childCenterOffset);
                this->children[5]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[6] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(childCenterOffset, childCenterOffset, -childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(childCenterOffset, childCenterOffset, -childCenterOffset);
                this->children[6]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -10.0 && this->children[7] != nullptr)
            {
                childBoundingBox.minCoords = bb.minCoords - B_Vector(childCenterOffset, childCenterOffset, childCenterOffset);
                childBoundingBox.maxCoords = bb.maxCoords - B_Vector(childCenterOffset, childCenterOffset, childCenterOffset);
                this->children[7]->CollectSectorsInBox(childBoundingBox, outList, childHalfSize);
            }
        }
    }
}

// address: 0x00453067
void B_OctTree::FindSectorsAtPoint(const B_Vector &worldPos, B_OctTreeSectorsList *outList) const
{
    outList->size = 0;
    B_Vector localPos = worldPos - this->m_center;
    gbl_oct_tree_query_id++;
    if (this->m_root != nullptr && fabs(localPos.x) < this->m_halfSize + 10.0 && fabs(localPos.y) < this->m_halfSize + 10.0 && fabs(localPos.z) < this->m_halfSize + 10.0)
    {
        this->m_root->CollectSectorsAtPoint(localPos, outList, this->m_halfSize);
    }
}

// address: 0x0045311A
void B_OctTree::FindSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *out) const
{
    out->size = 0;
    gbl_oct_tree_query_id++;
    gbl_current_query_box = &bb;
    B_BoundingBox localBB(bb.minCoords - this->m_center, bb.maxCoords - this->m_center);
    if (this->m_root != nullptr && localBB.maxCoords.x > -this->m_halfSize * 0.5 - 10.0 && localBB.maxCoords.y > -this->m_halfSize * 0.5 - 10.0 && localBB.maxCoords.z > -this->m_halfSize * 0.5 - 10.0 && localBB.minCoords.x < this->m_halfSize * 0.5 + 10.0 && localBB.minCoords.y < this->m_halfSize * 0.5 + 10.0 && localBB.minCoords.z < this->m_halfSize * 0.5 + 10.0)
    {
        this->m_root->CollectSectorsInBox(localBB, out, this->m_halfSize);
    }
}

// address: 0x00453264
B_OctTreeSectorsList::B_OctTreeSectorsList()
:
    size(0)
{
}

// address: 0x0045327B
int B_OctTreeSectorsList::BuildSurfaceCache(B_GlobalSurfaceCache *cache, const B_Sphere *sphere)
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
            if (distance < -sphere->radius)
            {
                j = current_sector->size + 1;
            }
            else if (distance < sphere->radius)
            {
                B_Surface *surface = current_sector->elements[j];
                cache->elements[cache->count].surfaces[cache->elements[cache->count].numSurfaces] = surface;
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

// address: 0x0045346F
B_SectorSurfaceCache::B_SectorSurfaceCache()
:
    numSurfaces(0)
{
}

// address: 0x00453490
B_SectorSurfaceCache::~B_SectorSurfaceCache()
{
}

// address: 0x004534A4
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

// address: 0x004539A9
B_GlobalSurfaceCache::B_GlobalSurfaceCache()
:
    count(0)
{
}

// address: 0x00453AC0
// B_OctantNodeBase: scalar deleting destructor

class B_OctantNodeBase
{
    // address: inline
    virtual ~B_OctantNodeBase()
    {
        gbl_node_count--;
    }
};
