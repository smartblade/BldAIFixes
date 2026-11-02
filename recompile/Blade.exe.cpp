
// address: 0x00401000
B_Sphere::B_Sphere()
{
    this->center.x = 0.0;
    this->center.y = 0.0;
    this->center.z = 0.0;
    this->radius = 0.0;
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
    double unknown_loc_18 = this->z - that.z;
    double unknown_loc_10 = this->y - that.y;
    double unknown_loc_08 = this->x - that.x;
    return B_Vector(unknown_loc_08, unknown_loc_10, unknown_loc_18);
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
{
    this->sectors = nullptr;
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
{
}

// address: 0x0045050B
B_SectorListNode::~B_SectorListNode()
{
}

// address: 0x004506B5
int B_SectorListNode::GetTypeID()
{
    return B_OCT_NODE_CID_SECTOR_LIST;
}

// address: 0x004507B9
B_OctTree::~B_OctTree()
{
    this->DeleteRoot();
}

// address: 0x004507D5
void B_OctTree::DeleteRoot()
{
    if (this->m_root != nullptr)
    {
        delete this->m_root;
        this->m_root = nullptr;
    }
}

// address: 0x0045201F
void LeafNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    if (this->sectors->lastQueryId != static_cast<int>(gbl_oct_tree_query_id) && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = static_cast<int>(gbl_oct_tree_query_id);
        if (outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}

// address: 0x00452082
void LeafNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
{
    if (this->sectors->lastQueryId != static_cast<int>(gbl_oct_tree_query_id) && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = static_cast<int>(gbl_oct_tree_query_id);
        B_BoundingBox *sectorBB = &this->sectors->boundingBox;
        if (!(gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x || gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y || gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z || gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x || gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y || gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z) && outList->size < 512)
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
        if (this->elements[i]->lastQueryId != static_cast<int>(gbl_oct_tree_query_id) && this->elements[i]->isActive != 0)
        {
            this->elements[i]->lastQueryId = static_cast<int>(gbl_oct_tree_query_id);
            if (outList->size < 512)
            {
                outList->sectors[outList->size] = this->elements[i];
                outList->size++;
            }
        }
    }
}

// address: 0x00452232
void B_SectorListNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
{
    for (unsigned int i = 0; i < this->size; i++)
    {
        if (this->elements[i]->lastQueryId != static_cast<int>(gbl_oct_tree_query_id) && this->elements[i]->isActive != 0)
        {
            this->elements[i]->lastQueryId = static_cast<int>(gbl_oct_tree_query_id);
            B_BoundingBox *sectorBB = &this->elements[i]->boundingBox;
            if (!(gbl_current_query_box->minCoords.x > sectorBB->maxCoords.x || gbl_current_query_box->minCoords.y > sectorBB->maxCoords.y || gbl_current_query_box->minCoords.z > sectorBB->maxCoords.z || gbl_current_query_box->maxCoords.x < sectorBB->minCoords.x || gbl_current_query_box->maxCoords.y < sectorBB->minCoords.y || gbl_current_query_box->maxCoords.z < sectorBB->minCoords.z) && outList->size < 512)
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
    double childHalfSize = halfSize / child_size_divisor;
    double childOffset = halfSize / child_offset_divisor;
    if (localPos.x < kOctTreeMargin)
    {
        if (localPos.y < kOctTreeMargin)
        {
            if (localPos.z < kOctTreeMargin && this->children[0] != nullptr)
            {
                B_Vector childCenter(-childOffset, -childOffset, -childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[0]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
            if (localPos.z > -kOctTreeMargin && this->children[1] != nullptr)
            {
                B_Vector childCenter(-childOffset, -childOffset, childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[1]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
        }
        if (localPos.y > -kOctTreeMargin)
        {
            if (localPos.z < kOctTreeMargin && this->children[2] != nullptr)
            {
                B_Vector childCenter(-childOffset, childOffset, -childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[2]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
            if (localPos.z > -kOctTreeMargin && this->children[3] != nullptr)
            {
                B_Vector childCenter(-childOffset, childOffset, childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[3]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
        }
    }
    if (localPos.x > -kOctTreeMargin)
    {
        if (localPos.y < kOctTreeMargin)
        {
            if (localPos.z < kOctTreeMargin && this->children[4] != nullptr)
            {
                B_Vector childCenter(childOffset, -childOffset, -childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[4]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
            if (localPos.z > -kOctTreeMargin && this->children[5] != nullptr)
            {
                B_Vector childCenter(childOffset, -childOffset, childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[5]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
        }
        if (localPos.y > -kOctTreeMargin)
        {
            if (localPos.z < kOctTreeMargin && this->children[6] != nullptr)
            {
                B_Vector childCenter(childOffset, childOffset, -childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[6]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
            if (localPos.z > -kOctTreeMargin && this->children[7] != nullptr)
            {
                B_Vector childCenter(childOffset, childOffset, childOffset);
                B_Vector newLocalPos = localPos - childCenter;
                this->children[7]->CollectSectorsAtPoint(newLocalPos, outList, childHalfSize);
            }
        }
    }
}

// address: 0x00452845
void B_OctantNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
{
    double childHalfSize = halfSize / child_size_divisor;
    double childOffset = halfSize / child_offset_divisor;
    B_BoundingBox childBox = bb;
    if (bb.minCoords.x < kOctTreeMargin)
    {
        if (bb.minCoords.y < kOctTreeMargin)
        {
            if (bb.minCoords.z < kOctTreeMargin && this->children[0] != nullptr)
            {
                B_Vector unknown_loc_58(-childOffset, -childOffset, -childOffset);
                B_Vector unknown_loc_70;
                childBox.minCoords = unknown_loc_70 = bb.minCoords - unknown_loc_58;
                B_Vector unknown_loc_88(-childOffset, -childOffset, -childOffset);
                B_Vector unknown_loc_A0;
                childBox.maxCoords = unknown_loc_A0 = bb.maxCoords - unknown_loc_88;
                this->children[0]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -kOctTreeMargin && this->children[1] != nullptr)
            {
                B_Vector unknown_loc_B8(-childOffset, -childOffset, childOffset);
                B_Vector unknown_loc_D0;
                childBox.minCoords = unknown_loc_D0 = bb.minCoords - unknown_loc_B8;
                B_Vector unknown_loc_E8(-childOffset, -childOffset, childOffset);
                B_Vector unknown_loc_100;
                childBox.maxCoords = unknown_loc_100 = bb.maxCoords - unknown_loc_E8;
                this->children[1]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
        }
        if (bb.maxCoords.y > -kOctTreeMargin)
        {
            if (bb.minCoords.z < kOctTreeMargin && this->children[2] != nullptr)
            {
                B_Vector unknown_loc_118(-childOffset, childOffset, -childOffset);
                B_Vector unknown_loc_130;
                childBox.minCoords = unknown_loc_130 = bb.minCoords - unknown_loc_118;
                B_Vector unknown_loc_148(-childOffset, childOffset, -childOffset);
                B_Vector unknown_loc_160;
                childBox.maxCoords = unknown_loc_160 = bb.maxCoords - unknown_loc_148;
                this->children[2]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -kOctTreeMargin && this->children[3] != nullptr)
            {
                B_Vector unknown_loc_178(-childOffset, childOffset, childOffset);
                B_Vector unknown_loc_190;
                childBox.minCoords = unknown_loc_190 = bb.minCoords - unknown_loc_178;
                B_Vector unknown_loc_1A8(-childOffset, childOffset, childOffset);
                B_Vector unknown_loc_1C0;
                childBox.maxCoords = unknown_loc_1C0 = bb.maxCoords - unknown_loc_1A8;
                this->children[3]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
        }
    }
    if (bb.maxCoords.x > -kOctTreeMargin)
    {
        if (bb.minCoords.y < kOctTreeMargin)
        {
            if (bb.minCoords.z < kOctTreeMargin && this->children[4] != nullptr)
            {
                B_Vector unknown_loc_1D8(childOffset, -childOffset, -childOffset);
                B_Vector unknown_loc_1F0;
                childBox.minCoords = unknown_loc_1F0 = bb.minCoords - unknown_loc_1D8;
                B_Vector unknown_loc_208(childOffset, -childOffset, -childOffset);
                B_Vector unknown_loc_220;
                childBox.maxCoords = unknown_loc_220 = bb.maxCoords - unknown_loc_208;
                this->children[4]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -kOctTreeMargin && this->children[5] != nullptr)
            {
                B_Vector unknown_loc_238(childOffset, -childOffset, childOffset);
                B_Vector unknown_loc_250;
                childBox.minCoords = unknown_loc_250 = bb.minCoords - unknown_loc_238;
                B_Vector unknown_loc_268(childOffset, -childOffset, childOffset);
                B_Vector unknown_loc_280;
                childBox.maxCoords = unknown_loc_280 = bb.maxCoords - unknown_loc_268;
                this->children[5]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
        }
        if (bb.maxCoords.y > -kOctTreeMargin)
        {
            if (bb.minCoords.z < kOctTreeMargin && this->children[6] != nullptr)
            {
                B_Vector unknown_loc_298(childOffset, childOffset, -childOffset);
                B_Vector unknown_loc_2B0;
                childBox.minCoords = unknown_loc_2B0 = bb.minCoords - unknown_loc_298;
                B_Vector unknown_loc_2C8(childOffset, childOffset, -childOffset);
                B_Vector unknown_loc_2E0;
                childBox.maxCoords = unknown_loc_2E0 = bb.maxCoords - unknown_loc_2C8;
                this->children[6]->CollectSectorsInBox(childBox, outList, childHalfSize);
            }
            if (bb.maxCoords.z > -kOctTreeMargin && this->children[7] != nullptr)
            {
                B_Vector unknown_loc_2F8(childOffset, childOffset, childOffset);
                B_Vector unknown_loc_310;
                childBox.minCoords = unknown_loc_310 = bb.minCoords - unknown_loc_2F8;
                B_Vector unknown_loc_328(childOffset, childOffset, childOffset);
                B_Vector unknown_loc_340;
                childBox.maxCoords = unknown_loc_340 = bb.maxCoords - unknown_loc_328;
                this->children[7]->CollectSectorsInBox(childBox, outList, childHalfSize);
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
    if (this->m_root != nullptr && this->m_halfSize + kOctTreeMargin > fabs(localPos.x) && this->m_halfSize + kOctTreeMargin > fabs(localPos.y) && this->m_halfSize + kOctTreeMargin > fabs(localPos.z))
    {
        this->m_root->CollectSectorsAtPoint(localPos, outList, this->m_halfSize);
    }
}

// address: 0x00453264
B_OctTreeSectorsList::B_OctTreeSectorsList()
{
    this->size = 0;
}

// address: 0x0045327B
int B_OctTreeSectorsList::BuildSurfaceCache(B_GlobalSurfaceCache *cache, const B_Sphere *sphere)
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
            double distance = sphere->center.z * current_surface->normal.z + sphere->center.y * current_surface->normal.y + sphere->center.x * current_surface->normal.x + current_surface->p;
            if (-sphere->radius > distance)
            {
                j = current_sector->size + 1;
            }
            else if (distance < sphere->radius)
            {
                B_Surface *unknown_loc_1C = current_sector->elements[j];
                cache->elements[cache->count].surfaces[cache->elements[cache->count].numSurfaces] = unknown_loc_1C;
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

// address: 0x004539A9
B_GlobalSurfaceCache::B_GlobalSurfaceCache()
{
    this->count = 0;
}

// address: 0x00453AC0
// p00453AC0: scalar deleting destructor
