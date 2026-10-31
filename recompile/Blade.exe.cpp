
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
{
    memcpy(this, &minCoords, 24);
    memcpy(&this->maxCoords, &maxCoords, 24);
}

// address: 0x0040A5D0
B_Vector B_Vector::operator -(const B_Vector &that) const
{
    STACKVAR(-24, 8) = this->z - that.z;
    STACKVAR(-16, 8) = this->y - that.y;
    STACKVAR(-8, 8) = this->x - that.x;
    __result->x = reinterpret_cast<double>(STACKVAR(-8, 8));
    __result->y = reinterpret_cast<double>(STACKVAR(-16, 8));
    __result->z = reinterpret_cast<double>(STACKVAR(-24, 8));
    REGDEF(eax=__result)
}

// address: 0x004501C1
void B_BoundingBox::CollectIntersectingSectors(const B_PtrArray<B_Sector> &sectors, B_PtrArray<B_Sector> &outBuffer)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < sectors.size; unknown_loc_04++)
    {
        B_Sector *unknown_loc_08 = reinterpret_cast<B_Sector *>(ACCESS(ARRPTR(sectors.elements, 4, unknown_loc_04, 0), 0, 4));
        if (this->Intersects(unknown_loc_08) == 0)
        {
            continue;
        }
        STACKVAR(-12, 4) = ACCESS(ARRPTR(sectors.elements, 4, unknown_loc_04, 0), 0, 4);
        if (outBuffer.num_alloc > outBuffer.size)
        {
            ACCESS(ARRPTR(outBuffer.elements, 4, outBuffer.size, 0), 0, 4) = STACKVAR(-12, 4);
            outBuffer.size++;
            continue;
        }
        outBuffer.num_alloc += reinterpret_cast<unsigned int>(outBuffer.increment);
        if (outBuffer.size == 0)
        {
            goto l004502DC;
        }
        STACKVAR(-24, 4) = unknown_function_005BBD38(4 * outBuffer.num_alloc);
        STACKVAR(-16, 4) = STACKVAR(-24, 4);
        for (unsigned int unknown_loc_14 = 0; unknown_loc_14 < outBuffer.size; unknown_loc_14++)
        {
            ACCESS(ARRPTR(STACKVAR(-16, 4), 4, unknown_loc_14, 0), 0, 4) = ACCESS(ARRPTR(outBuffer.elements, 4, unknown_loc_14, 0), 0, 4);
        }
        STACKVAR(-28, 4) = outBuffer.elements;
        unknown_function_005BBD3D(STACKVAR(-28, 4));
        outBuffer.elements = reinterpret_cast<TYPE **>(STACKVAR(-16, 4));
        goto l004502FA;
l004502DC:
        STACKVAR(-32, 4) = unknown_function_005BBD38(4 * outBuffer.num_alloc);
        outBuffer.elements = reinterpret_cast<TYPE **>(STACKVAR(-32, 4));
l004502FA:
        ACCESS(ARRPTR(outBuffer.elements, 4, outBuffer.size, 0), 0, 4) = STACKVAR(-12, 4);
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
            B_OctantNodeBase *unknown_loc_0C = this->children[unknown_loc_04];
            STACKVAR(-8, 4) = unknown_loc_0C;
            if (STACKVAR(-8, 4) != 0x00000000)
            {
                STACKVAR(-20, 4) = STACKVAR(-8, 4)->(ACCESS(ACCESS(STACKVAR(-8, 4), 0, 4), 4, 4))(0x00000001);
            }
            else
            {
                STACKVAR(-20, 4) = 0x00000000;
            }
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
        STACKVAR(-12, 4) = ACCESS(ARRPTR(ACCESS(STACKVAR(-20, 4), 4, 4), 4, unknown_loc_04, 0), 0, 4);
        STACKVAR(-8, 4) = STACKVAR(-12, 4);
        if (STACKVAR(-8, 4) != 0x00000000)
        {
            STACKVAR(-52, 4) = STACKVAR(-8, 4)->(ACCESS(ACCESS(STACKVAR(-8, 4), 0, 4), 0, 4))(0x00000001);
        }
        else
        {
            STACKVAR(-52, 4) = 0x00000000;
        }
    }
l00450596:
    STACKVAR(-16, 4) = ACCESS(STACKVAR(-20, 4), 4, 4);
    unknown_function_005BBD3D(STACKVAR(-16, 4));
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
        STACKVAR(-32, 4) = ACCESS(ARRPTR(ACCESS(STACKVAR(-44, 4), 4, 4), 4, unknown_loc_18, 0), 0, 4);
        STACKVAR(-28, 4) = STACKVAR(-32, 4);
        if (STACKVAR(-28, 4) != 0x00000000)
        {
            STACKVAR(-56, 4) = STACKVAR(-28, 4)->(ACCESS(ACCESS(STACKVAR(-28, 4), 0, 4), 0, 4))(0x00000001);
        }
        else
        {
            STACKVAR(-56, 4) = 0x00000000;
        }
    }
l00450666:
    STACKVAR(-36, 4) = ACCESS(STACKVAR(-44, 4), 4, 4);
    unknown_function_005BBD3D(STACKVAR(-36, 4));
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
        if ((gbl_current_query_box->minCoords.x > unknown_loc_04->maxCoords.x || gbl_current_query_box->minCoords.y > unknown_loc_04->maxCoords.y || gbl_current_query_box->minCoords.z > unknown_loc_04->maxCoords.z || gbl_current_query_box->maxCoords.x < unknown_loc_04->minCoords.x || gbl_current_query_box->maxCoords.y < unknown_loc_04->minCoords.y || gbl_current_query_box->maxCoords.z < unknown_loc_04->minCoords.z ? 0x00000000 : 0x00000001) != 0x00000000 && outList->size < 512)
        {
            outList->sectors[outList->size] = this->sectors;
            outList->size++;
        }
    }
}

// address: 0x00452191
void B_SectorListNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < reinterpret_cast<unsigned int>(ACCESS(this, 12, 4)); unknown_loc_04++)
    {
        if (reinterpret_cast<unsigned int>(ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 84, 4)) != gbl_oct_tree_query_id && ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 88, 4) != 0x00000000)
        {
            ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 84, 4) = gbl_oct_tree_query_id;
            if (outList->size < 512)
            {
                outList->sectors[outList->size] = reinterpret_cast<B_Sector *>(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4));
                outList->size++;
            }
        }
    }
}

// address: 0x00452232
void B_SectorListNode::CollectSectorsInBox(const B_BoundingBox &arg_1, B_OctTreeSectorsList *outList, double arg_3)
{
    for (unsigned int unknown_loc_04 = 0; unknown_loc_04 < reinterpret_cast<unsigned int>(ACCESS(this, 12, 4)); unknown_loc_04++)
    {
        if (reinterpret_cast<unsigned int>(ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 84, 4)) != gbl_oct_tree_query_id && ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 88, 4) != 0x00000000)
        {
            ACCESS(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4), 84, 4) = gbl_oct_tree_query_id;
            STACKVAR(-8, 4) = reinterpret_cast<any_int32>(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4)) + 0x0000005C;
            if ((gbl_current_query_box->minCoords.x > reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 24, 8)) || gbl_current_query_box->minCoords.y > reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 32, 8)) || gbl_current_query_box->minCoords.z > reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 40, 8)) || gbl_current_query_box->maxCoords.x < reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 0, 8)) || gbl_current_query_box->maxCoords.y < reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 8, 8)) || gbl_current_query_box->maxCoords.z < reinterpret_cast<double>(ACCESS(STACKVAR(-8, 4), 16, 8)) ? 0x00000000 : 0x00000001) != 0x00000000 && outList->size < 512)
            {
                outList->sectors[outList->size] = reinterpret_cast<B_Sector *>(ACCESS(ARRPTR(ACCESS(this, 8, 4), 4, unknown_loc_04, 0), 0, 4));
                outList->size++;
            }
        }
    }
}

// address: 0x00452388
void B_OctantNode::CollectSectorsAtPoint(const B_Vector &localPos, B_OctTreeSectorsList *outList, double halfSize)
{
    STACKVAR(-8, 8) = halfSize / 2.0;
    STACKVAR(-16, 8) = halfSize / 4.0;
    if (localPos.x < 10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[0] != nullptr)
            {
                STACKVAR(-40, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-32), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-24), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                this->children[0]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-64)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-40)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
            if (localPos.z > -10.0 && this->children[1] != nullptr)
            {
                STACKVAR(-88, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-80), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-72), 0, 8) = STACKVAR(-16, 8);
                this->children[1]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-112)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-88)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[2] != nullptr)
            {
                STACKVAR(-136, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-128), 0, 8) = STACKVAR(-16, 8);
                ACCESS(LOCAL(-120), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                this->children[2]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-160)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-136)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
            if (localPos.z > -10.0 && this->children[3] != nullptr)
            {
                STACKVAR(-184, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-176), 0, 8) = STACKVAR(-16, 8);
                ACCESS(LOCAL(-168), 0, 8) = STACKVAR(-16, 8);
                this->children[3]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-208)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-184)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
        }
    }
    if (localPos.x > -10.0)
    {
        if (localPos.y < 10.0)
        {
            if (localPos.z < 10.0 && this->children[4] != nullptr)
            {
                STACKVAR(-232, 4) = STACKVAR(-16, 4);
                STACKVAR(-228, 4) = STACKVAR(-12, 4);
                ACCESS(LOCAL(-224), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-216), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                this->children[4]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-256)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-232)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
            if (localPos.z > -10.0 && this->children[5] != nullptr)
            {
                STACKVAR(-280, 4) = STACKVAR(-16, 4);
                STACKVAR(-276, 4) = STACKVAR(-12, 4);
                ACCESS(LOCAL(-272), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                ACCESS(LOCAL(-264), 0, 8) = STACKVAR(-16, 8);
                this->children[5]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-304)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-280)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
        }
        if (localPos.y > -10.0)
        {
            if (localPos.z < 10.0 && this->children[6] != nullptr)
            {
                STACKVAR(-328, 4) = STACKVAR(-16, 4);
                STACKVAR(-324, 4) = STACKVAR(-12, 4);
                ACCESS(LOCAL(-320), 0, 8) = STACKVAR(-16, 8);
                ACCESS(LOCAL(-312), 0, 8) = -reinterpret_cast<double>(STACKVAR(-16, 8));
                this->children[6]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-352)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-328)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
            if (localPos.z > -10.0 && this->children[7] != nullptr)
            {
                STACKVAR(-376, 4) = STACKVAR(-16, 4);
                STACKVAR(-372, 4) = STACKVAR(-12, 4);
                ACCESS(LOCAL(-368), 0, 8) = STACKVAR(-16, 8);
                ACCESS(LOCAL(-360), 0, 8) = STACKVAR(-16, 8);
                this->children[7]->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-400)) = localPos - *reinterpret_cast<B_Vector *>(LOCAL(-376)), outList, reinterpret_cast<double>(STACKVAR(-8, 8)));
            }
        }
    }
}

// address: 0x00452845
void B_OctantNode::CollectSectorsInBox(const B_BoundingBox &bb, B_OctTreeSectorsList *outList, double halfSize)
{
    STACKVAR(-56, 8) = halfSize / 2.0;
    STACKVAR(-64, 8) = halfSize / 4.0;
    memcpy(LOCAL(-48), &bb, 48);
    if (bb.minCoords.x < 10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[0] != nullptr)
            {
                STACKVAR(-88, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-80), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-72), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-112)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-88))), 24);
                STACKVAR(-136, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-128), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-120), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-160)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-136))), 24);
                this->children[0]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
            if (bb.maxCoords.z > -10.0 && this->children[1] != nullptr)
            {
                STACKVAR(-184, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-176), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-168), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-208)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-184))), 24);
                STACKVAR(-232, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-224), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-216), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-256)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-232))), 24);
                this->children[1]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[2] != nullptr)
            {
                STACKVAR(-280, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-272), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-264), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-304)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-280))), 24);
                STACKVAR(-328, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-320), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-312), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-352)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-328))), 24);
                this->children[2]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
            if (bb.maxCoords.z > -10.0 && this->children[3] != nullptr)
            {
                STACKVAR(-376, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-368), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-360), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-400)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-376))), 24);
                STACKVAR(-424, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-416), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-408), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-448)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-424))), 24);
                this->children[3]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
        }
    }
    if (bb.maxCoords.x > -10.0)
    {
        if (bb.minCoords.y < 10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[4] != nullptr)
            {
                STACKVAR(-472, 4) = STACKVAR(-64, 4);
                STACKVAR(-468, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-464), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-456), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-496)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-472))), 24);
                STACKVAR(-520, 4) = STACKVAR(-64, 4);
                STACKVAR(-516, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-512), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-504), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-544)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-520))), 24);
                this->children[4]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
            if (bb.maxCoords.z > -10.0 && this->children[5] != nullptr)
            {
                STACKVAR(-568, 4) = STACKVAR(-64, 4);
                STACKVAR(-564, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-560), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-552), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-592)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-568))), 24);
                STACKVAR(-616, 4) = STACKVAR(-64, 4);
                STACKVAR(-612, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-608), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                ACCESS(LOCAL(-600), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-640)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-616))), 24);
                this->children[5]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
        }
        if (bb.maxCoords.y > -10.0)
        {
            if (bb.minCoords.z < 10.0 && this->children[6] != nullptr)
            {
                STACKVAR(-664, 4) = STACKVAR(-64, 4);
                STACKVAR(-660, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-656), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-648), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-688)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-664))), 24);
                STACKVAR(-712, 4) = STACKVAR(-64, 4);
                STACKVAR(-708, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-704), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-696), 0, 8) = -reinterpret_cast<double>(STACKVAR(-64, 8));
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-736)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-712))), 24);
                this->children[6]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
            if (bb.maxCoords.z > -10.0 && this->children[7] != nullptr)
            {
                STACKVAR(-760, 4) = STACKVAR(-64, 4);
                STACKVAR(-756, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-752), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-744), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-48), &(*reinterpret_cast<B_Vector *>(LOCAL(-784)) = *reinterpret_cast<B_Vector *>(&bb) - *reinterpret_cast<B_Vector *>(LOCAL(-760))), 24);
                STACKVAR(-808, 4) = STACKVAR(-64, 4);
                STACKVAR(-804, 4) = STACKVAR(-60, 4);
                ACCESS(LOCAL(-800), 0, 8) = STACKVAR(-64, 8);
                ACCESS(LOCAL(-792), 0, 8) = STACKVAR(-64, 8);
                memcpy(LOCAL(-24), &(*reinterpret_cast<B_Vector *>(LOCAL(-832)) = bb.maxCoords - *reinterpret_cast<B_Vector *>(LOCAL(-808))), 24);
                this->children[7]->CollectSectorsInBox(*reinterpret_cast<B_BoundingBox *>(LOCAL(-48)), outList, reinterpret_cast<double>(STACKVAR(-56, 8)));
            }
        }
    }
}

// address: 0x00453067
void B_OctTree::FindSectorsAtPoint(const B_Vector &worldPos, B_OctTreeSectorsList *outList) const
{
    outList->size = 0;
    *reinterpret_cast<B_Vector *>(LOCAL(-24)) = worldPos - this->m_center;
    gbl_oct_tree_query_id++;
    if (this->m_root != nullptr && this->m_halfSize + 10.0 > fabs(reinterpret_cast<double>(STACKVAR(-24, 8))) && this->m_halfSize + 10.0 > fabs(reinterpret_cast<double>(STACKVAR(-16, 8))) && this->m_halfSize + 10.0 > fabs(reinterpret_cast<double>(STACKVAR(-8, 8))))
    {
        this->m_root->CollectSectorsAtPoint(*reinterpret_cast<B_Vector *>(LOCAL(-24)), outList, this->m_halfSize);
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
        ACCESS(ARRPTR(cache, 1, 272 * cache->count, 8), 0, 4) = unknown_loc_10;
        ACCESS(ARRPTR(cache, 1, 272 * cache->count, 12), 0, 4) = 0x00000000;
        unsigned int unknown_loc_14;
        for (unknown_loc_14 = 0; unknown_loc_14 < unknown_loc_10->size; unknown_loc_14++)
        {
            STACKVAR(-24, 4) = ACCESS(ARRPTR(unknown_loc_10->elements, 4, unknown_loc_14, 0), 0, 4);
            STACKVAR(-8, 8) = sphere->center.z * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 20, 8)) + sphere->center.y * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 12, 8)) + sphere->center.x * reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 4, 8)) + reinterpret_cast<double>(ACCESS(STACKVAR(-24, 4), 28, 8));
            if (-sphere->radius > reinterpret_cast<double>(STACKVAR(-8, 8)))
            {
                unknown_loc_14 = unknown_loc_10->size + 1;
            }
            else if (reinterpret_cast<double>(STACKVAR(-8, 8)) < sphere->radius)
            {
                STACKVAR(-28, 4) = ACCESS(ARRPTR(unknown_loc_10->elements, 4, unknown_loc_14, 0), 0, 4);
                ACCESS(ARRPTR(reinterpret_cast<any_int32>(cache) + 272 * cache->count + 4, 4, ACCESS(ARRPTR(cache, 1, 272 * cache->count, 12), 0, 4), 12), 0, 4) = STACKVAR(-28, 4);
                ACCESS(ARRPTR(cache, 1, 272 * cache->count, 12), 0, 4) = reinterpret_cast<any_int32>(ACCESS(ARRPTR(cache, 1, 272 * cache->count, 12), 0, 4)) + 0x00000001;
            }
        }
        if (unknown_loc_14 == unknown_loc_10->size)
        {
            if (ACCESS(ARRPTR(cache, 1, 272 * cache->count, 12), 0, 4) == 0x00000000)
            {
                ACCESS(ARRPTR(cache, 1, 272 * cache->count, 272), 0, 4) = 0x00000001;
                cache->count++;
                return 1;
            }
            ACCESS(ARRPTR(cache, 1, 272 * cache->count, 272), 0, 4) = 0x00000000;
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
        unknown_function_005BBD3D(this);
    }
    REGDEF(eax=this)
}
