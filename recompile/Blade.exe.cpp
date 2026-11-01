
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
    __result->x = unknown_loc_08;
    __result->y = unknown_loc_10;
    __result->z = unknown_loc_18;
    REGDEF(eax=__result)
}

// address: 0x004501C1
void B_BoundingBox::CollectIntersectingSectors(const B_PtrArray<B_Sector> &sectors, B_PtrArray<B_Sector> &outBuffer)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < sectors.size; unknown_loc_04++)
    {
        B_Sector *unknown_loc_08 = sectors.elements[unknown_loc_04];
        if (this->Intersects(unknown_loc_08) == 0)
        {
            continue;
        }
        B_Sector *unknown_loc_0C = sectors.elements[unknown_loc_04];
        if (outBuffer.num_alloc > outBuffer.size)
        {
            outBuffer.elements[outBuffer.size] = unknown_loc_0C;
            outBuffer.size++;
            continue;
        }
        outBuffer.num_alloc += reinterpret_cast<unsigned int>(outBuffer.increment);
        if (outBuffer.size == 0)
        {
            goto l004502DC;
        }
        STACKVAR(-24, 4) = shi_new(4 * outBuffer.num_alloc);
        STACKVAR(-16, 4) = STACKVAR(-24, 4);
        for (unsigned int unknown_loc_14 = 0; unknown_loc_14 < outBuffer.size; unknown_loc_14++)
        {
            ACCESS(ARRPTR(STACKVAR(-16, 4), 4, unknown_loc_14, 0), 0, 4) = outBuffer.elements[unknown_loc_14];
        }
        STACKVAR(-28, 4) = outBuffer.elements;
        shi_delete(STACKVAR(-28, 4));
        outBuffer.elements = reinterpret_cast<B_Sector **>(STACKVAR(-16, 4));
        goto l004502FA;
l004502DC:
        STACKVAR(-32, 4) = shi_new(4 * outBuffer.num_alloc);
        outBuffer.elements = reinterpret_cast<B_Sector **>(STACKVAR(-32, 4));
l004502FA:
        outBuffer.elements[outBuffer.size] = unknown_loc_0C;
        outBuffer.size++;
    }
}

// address: 0x00450327
B_OctantNode::B_OctantNode()
{
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count++;
    ACCESS(this, 0, 4) = GLOBAL(0x005BDCFC);
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < 8; unknown_loc_04++)
    {
        this->children[unknown_loc_04] = nullptr;
    }
}

// address: 0x00450380
B_OctantNode::~B_OctantNode()
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < 8; unknown_loc_04++)
    {
        if (this->children[unknown_loc_04] != nullptr)
        {
            delete this->children[unknown_loc_04];
        }
    }
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count--;
}

// address: 0x00450407
int B_OctantNode::GetTypeID()
{
    return B_OCT_NODE_CID_BRANCH;
}

// address: 0x00450417
LeafNode::LeafNode()
{
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count++;
    this->sectors = nullptr;
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD1C);
}

// address: 0x00450450
LeafNode::~LeafNode()
{
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count--;
}

// address: 0x0045047C
int LeafNode::GetTypeID()
{
    return B_OCT_NODE_CID_LEAF;
}

// address: 0x0045048C
B_SectorListNode::B_SectorListNode()
{
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count++;
    STACKVAR(-4, 4) = reinterpret_cast<any_int32>(this) + 0x00000004;
    ACCESS(STACKVAR(-4, 4), 4, 4) = 0x00000000;
    ACCESS(STACKVAR(-4, 4), 8, 4) = 0x00000000;
    ACCESS(STACKVAR(-4, 4), 12, 4) = 0x00000001;
    ACCESS(STACKVAR(-4, 4), 16, 4) = 0x00000000;
    ACCESS(STACKVAR(-4, 4), 20, 4) = 0x00000001;
    ACCESS(STACKVAR(-4, 4), 0, 4) = GLOBAL(0x005BDB7C);
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD30);
    ACCESS(this, 4, 4) = GLOBAL(0x005BDD2C);
}

// address: 0x0045050B
B_SectorListNode::~B_SectorListNode()
{
    ACCESS(this, 4, 4) = GLOBAL(0x005BDD2C);
    STACKVAR(-20, 4) = reinterpret_cast<any_int32>(this) + 0x00000004;
    if (ACCESS(STACKVAR(-20, 4), 16, 4) == 0x00000000)
    {
        goto l004505C9;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00450596;
    }
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < reinterpret_cast<unsigned int>(ACCESS(STACKVAR(-20, 4), 8, 4)); unknown_loc_04++)
    {
        delete ACCESS(ARRPTR(ACCESS(STACKVAR(-20, 4), 4, 4), 4, unknown_loc_04, 0), 0, 4);
    }
l00450596:
    STACKVAR(-16, 4) = ACCESS(STACKVAR(-20, 4), 4, 4);
    shi_delete(STACKVAR(-16, 4));
    ACCESS(STACKVAR(-20, 4), 4, 4) = 0x00000000;
    ACCESS(STACKVAR(-20, 4), 8, 4) = 0x00000000;
    ACCESS(STACKVAR(-20, 4), 16, 4) = 0x00000000;
l004505C9:
    if (this != nullptr)
    {
        STACKVAR(-44, 4) = reinterpret_cast<any_int32>(this) + 0x00000004;
    }
    else
    {
        STACKVAR(-44, 4) = 0x00000000;
    }
    ACCESS(STACKVAR(-44, 4), 0, 4) = GLOBAL(0x005BDB7C);
    if (ACCESS(STACKVAR(-44, 4), 16, 4) == 0x00000000)
    {
        goto l00450699;
    }
    STACKVAR(-40, 4) = ACCESS(STACKVAR(-44, 4), 20, 4);
    if (ACCESS(STACKVAR(-44, 4), 16, 4) == 0x00000000)
    {
        goto l00450699;
    }
    if (STACKVAR(-40, 4) == 0x00000000)
    {
        goto l00450666;
    }
    for (unsigned int unknown_loc_18 = 0; unknown_loc_18 < reinterpret_cast<unsigned int>(ACCESS(STACKVAR(-44, 4), 8, 4)); unknown_loc_18++)
    {
        delete ACCESS(ARRPTR(ACCESS(STACKVAR(-44, 4), 4, 4), 4, unknown_loc_18, 0), 0, 4);
    }
l00450666:
    STACKVAR(-36, 4) = ACCESS(STACKVAR(-44, 4), 4, 4);
    shi_delete(STACKVAR(-36, 4));
    ACCESS(STACKVAR(-44, 4), 4, 4) = 0x00000000;
    ACCESS(STACKVAR(-44, 4), 8, 4) = 0x00000000;
    ACCESS(STACKVAR(-44, 4), 16, 4) = 0x00000000;
l00450699:
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count--;
}

// address: 0x004506B5
int B_SectorListNode::GetTypeID()
{
    return B_OCT_NODE_CID_SECTOR_LIST;
}

// address: 0x004507B9
B_OctTree::~B_OctTree()
{
    this->unknown_method_004507D5();
}

// address: 0x0045201F
void LeafNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    if (this->sectors->lastQueryId != reinterpret_cast<int>(gbl_oct_tree_query_id) && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = reinterpret_cast<int>(gbl_oct_tree_query_id);
        if (outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}

// address: 0x00452082
void LeafNode::CollectSectorsInBox(const B_BoundingBox &arg_1, B_OctTreeSectorsList *outList, double arg_3)
{
    if (this->sectors->lastQueryId != reinterpret_cast<int>(gbl_oct_tree_query_id) && this->sectors->isActive != 0)
    {
        this->sectors->lastQueryId = reinterpret_cast<int>(gbl_oct_tree_query_id);
        B_BoundingBox *unknown_loc_04 = &this->sectors->boundingBox;
        if (!(gbl_current_query_box->minCoords.x > unknown_loc_04->maxCoords.x || gbl_current_query_box->minCoords.y > unknown_loc_04->maxCoords.y || gbl_current_query_box->minCoords.z > unknown_loc_04->maxCoords.z || gbl_current_query_box->maxCoords.x < unknown_loc_04->minCoords.x || gbl_current_query_box->maxCoords.y < unknown_loc_04->minCoords.y || gbl_current_query_box->maxCoords.z < unknown_loc_04->minCoords.z) && outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}

// address: 0x00452191
void B_SectorListNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < this->size; unknown_loc_04++)
    {
        if (this->elements[unknown_loc_04]->lastQueryId != reinterpret_cast<int>(gbl_oct_tree_query_id) && this->elements[unknown_loc_04]->isActive != 0)
        {
            this->elements[unknown_loc_04]->lastQueryId = reinterpret_cast<int>(gbl_oct_tree_query_id);
            if (outList->size < 512)
            {
                outList->sectors[outList->size] = this->elements[unknown_loc_04];
                outList->size++;
            }
        }
    }
}

// address: 0x00452232
void B_SectorListNode::CollectSectorsInBox(const B_BoundingBox &arg_1, B_OctTreeSectorsList *outList, double arg_3)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < this->size; unknown_loc_04++)
    {
        if (this->elements[unknown_loc_04]->lastQueryId != reinterpret_cast<int>(gbl_oct_tree_query_id) && this->elements[unknown_loc_04]->isActive != 0)
        {
            this->elements[unknown_loc_04]->lastQueryId = reinterpret_cast<int>(gbl_oct_tree_query_id);
            B_BoundingBox *unknown_loc_08 = &this->elements[unknown_loc_04]->boundingBox;
            if (!(gbl_current_query_box->minCoords.x > unknown_loc_08->maxCoords.x || gbl_current_query_box->minCoords.y > unknown_loc_08->maxCoords.y || gbl_current_query_box->minCoords.z > unknown_loc_08->maxCoords.z || gbl_current_query_box->maxCoords.x < unknown_loc_08->minCoords.x || gbl_current_query_box->maxCoords.y < unknown_loc_08->minCoords.y || gbl_current_query_box->maxCoords.z < unknown_loc_08->minCoords.z) && outList->size < 512)
            {
                outList->sectors[outList->size] = this->elements[unknown_loc_04];
                outList->size++;
            }
        }
    }
}

// address: 0x00452388
void B_OctantNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    double unknown_loc_08 = halfSize / 2.0;
    double unknown_loc_10 = halfSize / 4.0;
    if (localPos.x < 10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[0] != nullptr)
            {
                B_Vector unknown_loc_28;
                unknown_loc_28.x = -unknown_loc_10;
                unknown_loc_28.y = -unknown_loc_10;
                unknown_loc_28.z = -unknown_loc_10;
                B_Vector unknown_loc_40;
                this->children[0]->CollectSectorsAtPoint(unknown_loc_40 = localPos - unknown_loc_28, outList, unknown_loc_08);
            }
            if (localPos.z > -10.0 && this->children[1] != nullptr)
            {
                B_Vector unknown_loc_58;
                unknown_loc_58.x = -unknown_loc_10;
                unknown_loc_58.y = -unknown_loc_10;
                unknown_loc_58.z = unknown_loc_10;
                B_Vector unknown_loc_70;
                this->children[1]->CollectSectorsAtPoint(unknown_loc_70 = localPos - unknown_loc_58, outList, unknown_loc_08);
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[2] != nullptr)
            {
                B_Vector unknown_loc_88;
                unknown_loc_88.x = -unknown_loc_10;
                unknown_loc_88.y = unknown_loc_10;
                unknown_loc_88.z = -unknown_loc_10;
                B_Vector unknown_loc_A0;
                this->children[2]->CollectSectorsAtPoint(unknown_loc_A0 = localPos - unknown_loc_88, outList, unknown_loc_08);
            }
            if (localPos.z > -10.0 && this->children[3] != nullptr)
            {
                B_Vector unknown_loc_B8;
                unknown_loc_B8.x = -unknown_loc_10;
                unknown_loc_B8.y = unknown_loc_10;
                unknown_loc_B8.z = unknown_loc_10;
                B_Vector unknown_loc_D0;
                this->children[3]->CollectSectorsAtPoint(unknown_loc_D0 = localPos - unknown_loc_B8, outList, unknown_loc_08);
            }
        }
    }
    if (localPos.x > -10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[4] != nullptr)
            {
                B_Vector unknown_loc_E8;
                unknown_loc_E8.x = unknown_loc_10;
                unknown_loc_E8.y = -unknown_loc_10;
                unknown_loc_E8.z = -unknown_loc_10;
                B_Vector unknown_loc_100;
                this->children[4]->CollectSectorsAtPoint(unknown_loc_100 = localPos - unknown_loc_E8, outList, unknown_loc_08);
            }
            if (localPos.z > -10.0 && this->children[5] != nullptr)
            {
                B_Vector unknown_loc_118;
                unknown_loc_118.x = unknown_loc_10;
                unknown_loc_118.y = -unknown_loc_10;
                unknown_loc_118.z = unknown_loc_10;
                B_Vector unknown_loc_130;
                this->children[5]->CollectSectorsAtPoint(unknown_loc_130 = localPos - unknown_loc_118, outList, unknown_loc_08);
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[6] != nullptr)
            {
                B_Vector unknown_loc_148;
                unknown_loc_148.x = unknown_loc_10;
                unknown_loc_148.y = unknown_loc_10;
                unknown_loc_148.z = -unknown_loc_10;
                B_Vector unknown_loc_160;
                this->children[6]->CollectSectorsAtPoint(unknown_loc_160 = localPos - unknown_loc_148, outList, unknown_loc_08);
            }
            if (localPos.z > -10.0 && this->children[7] != nullptr)
            {
                B_Vector unknown_loc_178;
                unknown_loc_178.x = unknown_loc_10;
                unknown_loc_178.y = unknown_loc_10;
                unknown_loc_178.z = unknown_loc_10;
                B_Vector unknown_loc_190;
                this->children[7]->CollectSectorsAtPoint(unknown_loc_190 = localPos - unknown_loc_178, outList, unknown_loc_08);
            }
        }
    }
}

// address: 0x00452845
void B_OctantNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
{
    double unknown_loc_38 = halfSize / 2.0;
    double unknown_loc_40 = halfSize / 4.0;
    B_BoundingBox unknown_loc_30 = bb;
    if (bb.minCoords.x < 10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[0] != nullptr)
            {
                B_Vector unknown_loc_58;
                unknown_loc_58.x = -unknown_loc_40;
                unknown_loc_58.y = -unknown_loc_40;
                unknown_loc_58.z = -unknown_loc_40;
                B_Vector unknown_loc_70;
                unknown_loc_30.minCoords = unknown_loc_70 = bb.minCoords - unknown_loc_58;
                B_Vector unknown_loc_88;
                unknown_loc_88.x = -unknown_loc_40;
                unknown_loc_88.y = -unknown_loc_40;
                unknown_loc_88.z = -unknown_loc_40;
                B_Vector unknown_loc_A0;
                unknown_loc_30.maxCoords = unknown_loc_A0 = bb.maxCoords - unknown_loc_88;
                this->children[0]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
            if (bb.maxCoords.z > -10.0 && this->children[1] != nullptr)
            {
                B_Vector unknown_loc_B8;
                unknown_loc_B8.x = -unknown_loc_40;
                unknown_loc_B8.y = -unknown_loc_40;
                unknown_loc_B8.z = unknown_loc_40;
                B_Vector unknown_loc_D0;
                unknown_loc_30.minCoords = unknown_loc_D0 = bb.minCoords - unknown_loc_B8;
                B_Vector unknown_loc_E8;
                unknown_loc_E8.x = -unknown_loc_40;
                unknown_loc_E8.y = -unknown_loc_40;
                unknown_loc_E8.z = unknown_loc_40;
                B_Vector unknown_loc_100;
                unknown_loc_30.maxCoords = unknown_loc_100 = bb.maxCoords - unknown_loc_E8;
                this->children[1]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[2] != nullptr)
            {
                B_Vector unknown_loc_118;
                unknown_loc_118.x = -unknown_loc_40;
                unknown_loc_118.y = unknown_loc_40;
                unknown_loc_118.z = -unknown_loc_40;
                B_Vector unknown_loc_130;
                unknown_loc_30.minCoords = unknown_loc_130 = bb.minCoords - unknown_loc_118;
                B_Vector unknown_loc_148;
                unknown_loc_148.x = -unknown_loc_40;
                unknown_loc_148.y = unknown_loc_40;
                unknown_loc_148.z = -unknown_loc_40;
                B_Vector unknown_loc_160;
                unknown_loc_30.maxCoords = unknown_loc_160 = bb.maxCoords - unknown_loc_148;
                this->children[2]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
            if (bb.maxCoords.z > -10.0 && this->children[3] != nullptr)
            {
                B_Vector unknown_loc_178;
                unknown_loc_178.x = -unknown_loc_40;
                unknown_loc_178.y = unknown_loc_40;
                unknown_loc_178.z = unknown_loc_40;
                B_Vector unknown_loc_190;
                unknown_loc_30.minCoords = unknown_loc_190 = bb.minCoords - unknown_loc_178;
                B_Vector unknown_loc_1A8;
                unknown_loc_1A8.x = -unknown_loc_40;
                unknown_loc_1A8.y = unknown_loc_40;
                unknown_loc_1A8.z = unknown_loc_40;
                B_Vector unknown_loc_1C0;
                unknown_loc_30.maxCoords = unknown_loc_1C0 = bb.maxCoords - unknown_loc_1A8;
                this->children[3]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
        }
    }
    if (bb.maxCoords.x > -10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[4] != nullptr)
            {
                B_Vector unknown_loc_1D8;
                unknown_loc_1D8.x = unknown_loc_40;
                unknown_loc_1D8.y = -unknown_loc_40;
                unknown_loc_1D8.z = -unknown_loc_40;
                B_Vector unknown_loc_1F0;
                unknown_loc_30.minCoords = unknown_loc_1F0 = bb.minCoords - unknown_loc_1D8;
                B_Vector unknown_loc_208;
                unknown_loc_208.x = unknown_loc_40;
                unknown_loc_208.y = -unknown_loc_40;
                unknown_loc_208.z = -unknown_loc_40;
                B_Vector unknown_loc_220;
                unknown_loc_30.maxCoords = unknown_loc_220 = bb.maxCoords - unknown_loc_208;
                this->children[4]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
            if (bb.maxCoords.z > -10.0 && this->children[5] != nullptr)
            {
                B_Vector unknown_loc_238;
                unknown_loc_238.x = unknown_loc_40;
                unknown_loc_238.y = -unknown_loc_40;
                unknown_loc_238.z = unknown_loc_40;
                B_Vector unknown_loc_250;
                unknown_loc_30.minCoords = unknown_loc_250 = bb.minCoords - unknown_loc_238;
                B_Vector unknown_loc_268;
                unknown_loc_268.x = unknown_loc_40;
                unknown_loc_268.y = -unknown_loc_40;
                unknown_loc_268.z = unknown_loc_40;
                B_Vector unknown_loc_280;
                unknown_loc_30.maxCoords = unknown_loc_280 = bb.maxCoords - unknown_loc_268;
                this->children[5]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[6] != nullptr)
            {
                B_Vector unknown_loc_298;
                unknown_loc_298.x = unknown_loc_40;
                unknown_loc_298.y = unknown_loc_40;
                unknown_loc_298.z = -unknown_loc_40;
                B_Vector unknown_loc_2B0;
                unknown_loc_30.minCoords = unknown_loc_2B0 = bb.minCoords - unknown_loc_298;
                B_Vector unknown_loc_2C8;
                unknown_loc_2C8.x = unknown_loc_40;
                unknown_loc_2C8.y = unknown_loc_40;
                unknown_loc_2C8.z = -unknown_loc_40;
                B_Vector unknown_loc_2E0;
                unknown_loc_30.maxCoords = unknown_loc_2E0 = bb.maxCoords - unknown_loc_2C8;
                this->children[6]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
            if (bb.maxCoords.z > -10.0 && this->children[7] != nullptr)
            {
                B_Vector unknown_loc_2F8;
                unknown_loc_2F8.x = unknown_loc_40;
                unknown_loc_2F8.y = unknown_loc_40;
                unknown_loc_2F8.z = unknown_loc_40;
                B_Vector unknown_loc_310;
                unknown_loc_30.minCoords = unknown_loc_310 = bb.minCoords - unknown_loc_2F8;
                B_Vector unknown_loc_328;
                unknown_loc_328.x = unknown_loc_40;
                unknown_loc_328.y = unknown_loc_40;
                unknown_loc_328.z = unknown_loc_40;
                B_Vector unknown_loc_340;
                unknown_loc_30.maxCoords = unknown_loc_340 = bb.maxCoords - unknown_loc_328;
                this->children[7]->CollectSectorsInBox(unknown_loc_30, outList, unknown_loc_38);
            }
        }
    }
}

// address: 0x00453067
void B_OctTree::FindSectorsAtPoint(const B_Vector &worldPos, B_OctTreeSectorsList *outList) const
{
    outList->size = 0;
    B_Vector unknown_loc_18;
    unknown_loc_18 = worldPos - this->m_center;
    gbl_oct_tree_query_id++;
    if (this->m_root != nullptr && this->m_halfSize + 10.0 > fabs(unknown_loc_18.x) && this->m_halfSize + 10.0 > fabs(unknown_loc_18.y) && this->m_halfSize + 10.0 > fabs(unknown_loc_18.z))
    {
        this->m_root->CollectSectorsAtPoint(unknown_loc_18, outList, this->m_halfSize);
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
    unsigned int unknown_loc_0C = 0;
    for (unknown_loc_0C = 0; unknown_loc_0C < this->size; unknown_loc_0C++)
    {
        B_Sector *unknown_loc_10 = this->sectors[unknown_loc_0C];
        cache->elements[cache->count].sector = unknown_loc_10;
        cache->elements[cache->count].numSurfaces = 0;
        unsigned int unknown_loc_14;
        for (unknown_loc_14 = 0; unknown_loc_14 < unknown_loc_10->size; unknown_loc_14++)
        {
            STACKVAR(-24, 4) = unknown_loc_10->elements[unknown_loc_14];
            double unknown_loc_08 = sphere->center.z * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 20, 8)) + sphere->center.y * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 12, 8)) + sphere->center.x * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 4, 8)) + reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 28, 8));
            if (-sphere->radius > unknown_loc_08)
            {
                unknown_loc_14 = unknown_loc_10->size + 1;
            }
            else if (unknown_loc_08 < sphere->radius)
            {
                STACKVAR(-28, 4) = unknown_loc_10->elements[unknown_loc_14];
                ACCESS(ARRPTR(reinterpret_cast<any_int32>(cache) + 272 * cache->count + 4, 4, cache->elements[cache->count].numSurfaces, 12), 0, 4) = STACKVAR(-28, 4);
                cache->elements[cache->count].numSurfaces++;
            }
        }
        if (unknown_loc_14 == unknown_loc_10->size)
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
    int unknown_loc_0C = 128;
    STACKVAR(-8, 4) = 0x00000110;
    STACKVAR(-4, 4) = &this->elements;
    while (--unknown_loc_0C >= 0)
    {
        reinterpret_cast<B_SectorSurfaceCache *>(STACKVAR(-4, 4))->B_SectorSurfaceCache();
        STACKVAR(-4, 4) = reinterpret_cast<any_int32>(STACKVAR(-4, 4)) + reinterpret_cast<any_int32>(STACKVAR(-8, 4));
    }
}

// address: 0x00453AC0
p00453AC0
{
    ProcedureInfo(this=Id(this), this_offset=-4, local_size=4, stack_delta=4)
    ACCESS(this, 0, 4) = GLOBAL(0x005BDD0C);
    gbl_node_count--;
    if ((reinterpret_cast<any_int32>(STACKVAR(8, 4)) & 0x00000001) != 0x00000000)
    {
        shi_delete(this);
    }
    REGDEF(eax=this)
}
