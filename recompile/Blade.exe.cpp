
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
    LeafNode *unknown_loc_04;
    B_Sector *unknown_loc_1BC;
    B_Sector *unknown_loc_1C0;
    if (map.size == 0)
    {
        return nullptr;
    }
    if (map.size == 1)
    {
        unknown_loc_04 = new LeafNode();
        unknown_loc_1BC = reinterpret_cast<B_Sector *>(ACCESS(ARRPTR(map.elements, 1, 0x00000004 * 0x00000000, 0), 0, 4));
        unknown_loc_04->sectors = unknown_loc_1BC;
        return unknown_loc_04;
    }
    if (worldBB.maxCoords.x - worldBB.minCoords.x >= sizeThreshold && map.size >= 8)
    {
        goto l00450ABC;
    }
    STACKVAR(-12, 4) = new B_SectorListNode();
    for (unsigned int unknown_loc_08 = 0; unknown_loc_08 < map.size; unknown_loc_08++)
    {
        unknown_loc_1C0 = map.elements[unknown_loc_08];
        STACKVAR(-472, 4) = reinterpret_cast<any_int32>(STACKVAR(-12, 4)) + 0x00000004;
        STACKVAR(-472, 4)->Append(unknown_loc_1C0);
    }
    return reinterpret_cast<B_OctantNodeBase *>(STACKVAR(-12, 4));
l00450ABC:
    B_BoundingBox unknown_loc_6C;
    unknown_loc_6C.B_BoundingBox();
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-48, 4) = 0x00000010;
    STACKVAR(-44, 4) = 0x00000000;
    STACKVAR(-40, 4) = 0x00000001;
    STACKVAR(-60, 4) = GLOBAL(0x005BDB7C);
    B_OctantNode *unknown_loc_70 = new B_OctantNode();
    *reinterpret_cast<B_Vector *>(LOCAL(-36)) = (worldBB.minCoords + worldBB.maxCoords) * 0.5;
    unknown_loc_6C.minCoords = worldBB.minCoords;
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-36), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[0] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00450C45;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00450C18;
    }
    for (unsigned int unknown_loc_1DC = 0; unknown_loc_1DC < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_1DC++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_1DC, 0), 0, 4);
    }
l00450C18:
    STACKVAR(-488, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-488, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00450C45:
    STACKVAR(-512, 4) = STACKVAR(-20, 4);
    STACKVAR(-508, 4) = STACKVAR(-16, 4);
    double unknown_loc_1F8 = worldBB.minCoords.y;
    double unknown_loc_1F0 = worldBB.minCoords.x;
    STACKVAR(-172, 8) = unknown_loc_1F0;
    ACCESS(LOCAL(-164), 0, 8) = unknown_loc_1F8;
    ACCESS(LOCAL(-156), 0, 8) = STACKVAR(-512, 8);
    memcpy(&unknown_loc_6C, LOCAL(-172), 24);
    double unknown_loc_218 = worldBB.maxCoords.z;
    STACKVAR(-528, 4) = STACKVAR(-28, 4);
    STACKVAR(-524, 4) = STACKVAR(-24, 4);
    STACKVAR(-520, 4) = STACKVAR(-36, 4);
    STACKVAR(-516, 4) = STACKVAR(-32, 4);
    STACKVAR(-196, 4) = STACKVAR(-520, 4);
    STACKVAR(-192, 4) = STACKVAR(-516, 4);
    ACCESS(LOCAL(-188), 0, 8) = STACKVAR(-528, 8);
    ACCESS(LOCAL(-180), 0, 8) = unknown_loc_218;
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-196), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[1] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00450E44;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00450E17;
    }
    for (unsigned int unknown_loc_21C = 0; unknown_loc_21C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_21C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_21C, 0), 0, 4);
    }
l00450E17:
    STACKVAR(-552, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-552, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00450E44:
    double unknown_loc_240 = worldBB.minCoords.z;
    STACKVAR(-568, 4) = STACKVAR(-28, 4);
    STACKVAR(-564, 4) = STACKVAR(-24, 4);
    double unknown_loc_230 = worldBB.minCoords.x;
    STACKVAR(-220, 8) = unknown_loc_230;
    ACCESS(LOCAL(-212), 0, 8) = STACKVAR(-568, 8);
    ACCESS(LOCAL(-204), 0, 8) = unknown_loc_240;
    memcpy(&unknown_loc_6C, LOCAL(-220), 24);
    STACKVAR(-600, 4) = STACKVAR(-20, 4);
    STACKVAR(-596, 4) = STACKVAR(-16, 4);
    double unknown_loc_250 = worldBB.maxCoords.y;
    STACKVAR(-584, 4) = STACKVAR(-36, 4);
    STACKVAR(-580, 4) = STACKVAR(-32, 4);
    STACKVAR(-244, 4) = STACKVAR(-584, 4);
    STACKVAR(-240, 4) = STACKVAR(-580, 4);
    ACCESS(LOCAL(-236), 0, 8) = unknown_loc_250;
    ACCESS(LOCAL(-228), 0, 8) = STACKVAR(-600, 8);
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-244), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[2] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451043;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451016;
    }
    for (unsigned int unknown_loc_25C = 0; unknown_loc_25C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_25C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_25C, 0), 0, 4);
    }
l00451016:
    STACKVAR(-616, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-616, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451043:
    STACKVAR(-640, 4) = STACKVAR(-20, 4);
    STACKVAR(-636, 4) = STACKVAR(-16, 4);
    STACKVAR(-632, 4) = STACKVAR(-28, 4);
    STACKVAR(-628, 4) = STACKVAR(-24, 4);
    double unknown_loc_270 = worldBB.minCoords.x;
    STACKVAR(-268, 8) = unknown_loc_270;
    ACCESS(LOCAL(-260), 0, 8) = STACKVAR(-632, 8);
    ACCESS(LOCAL(-252), 0, 8) = STACKVAR(-640, 8);
    memcpy(&unknown_loc_6C, LOCAL(-268), 24);
    double unknown_loc_298 = worldBB.maxCoords.z;
    double unknown_loc_290 = worldBB.maxCoords.y;
    STACKVAR(-648, 4) = STACKVAR(-36, 4);
    STACKVAR(-644, 4) = STACKVAR(-32, 4);
    STACKVAR(-292, 4) = STACKVAR(-648, 4);
    STACKVAR(-288, 4) = STACKVAR(-644, 4);
    ACCESS(LOCAL(-284), 0, 8) = unknown_loc_290;
    ACCESS(LOCAL(-276), 0, 8) = unknown_loc_298;
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-292), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[3] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451242;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451215;
    }
    for (unsigned int unknown_loc_29C = 0; unknown_loc_29C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_29C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_29C, 0), 0, 4);
    }
l00451215:
    STACKVAR(-680, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-680, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451242:
    double unknown_loc_2C0 = worldBB.minCoords.z;
    double unknown_loc_2B8 = worldBB.minCoords.y;
    STACKVAR(-688, 4) = STACKVAR(-36, 4);
    STACKVAR(-684, 4) = STACKVAR(-32, 4);
    STACKVAR(-316, 4) = STACKVAR(-688, 4);
    STACKVAR(-312, 4) = STACKVAR(-684, 4);
    ACCESS(LOCAL(-308), 0, 8) = unknown_loc_2B8;
    ACCESS(LOCAL(-300), 0, 8) = unknown_loc_2C0;
    memcpy(&unknown_loc_6C, LOCAL(-316), 24);
    STACKVAR(-728, 4) = STACKVAR(-20, 4);
    STACKVAR(-724, 4) = STACKVAR(-16, 4);
    STACKVAR(-720, 4) = STACKVAR(-28, 4);
    STACKVAR(-716, 4) = STACKVAR(-24, 4);
    double unknown_loc_2C8 = worldBB.maxCoords.x;
    STACKVAR(-340, 8) = unknown_loc_2C8;
    ACCESS(LOCAL(-332), 0, 8) = STACKVAR(-720, 8);
    ACCESS(LOCAL(-324), 0, 8) = STACKVAR(-728, 8);
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-340), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[4] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451442;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451415;
    }
    for (unsigned int unknown_loc_2DC = 0; unknown_loc_2DC < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_2DC++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_2DC, 0), 0, 4);
    }
l00451415:
    STACKVAR(-744, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-744, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451442:
    STACKVAR(-768, 4) = STACKVAR(-20, 4);
    STACKVAR(-764, 4) = STACKVAR(-16, 4);
    double unknown_loc_2F8 = worldBB.minCoords.y;
    STACKVAR(-752, 4) = STACKVAR(-36, 4);
    STACKVAR(-748, 4) = STACKVAR(-32, 4);
    STACKVAR(-364, 4) = STACKVAR(-752, 4);
    STACKVAR(-360, 4) = STACKVAR(-748, 4);
    ACCESS(LOCAL(-356), 0, 8) = unknown_loc_2F8;
    ACCESS(LOCAL(-348), 0, 8) = STACKVAR(-768, 8);
    memcpy(&unknown_loc_6C, LOCAL(-364), 24);
    double unknown_loc_318 = worldBB.maxCoords.z;
    STACKVAR(-784, 4) = STACKVAR(-28, 4);
    STACKVAR(-780, 4) = STACKVAR(-24, 4);
    double unknown_loc_308 = worldBB.maxCoords.x;
    STACKVAR(-388, 8) = unknown_loc_308;
    ACCESS(LOCAL(-380), 0, 8) = STACKVAR(-784, 8);
    ACCESS(LOCAL(-372), 0, 8) = unknown_loc_318;
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-388), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[5] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451642;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451615;
    }
    for (unsigned int unknown_loc_31C = 0; unknown_loc_31C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_31C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_31C, 0), 0, 4);
    }
l00451615:
    STACKVAR(-808, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-808, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451642:
    double unknown_loc_340 = worldBB.minCoords.z;
    STACKVAR(-824, 4) = STACKVAR(-28, 4);
    STACKVAR(-820, 4) = STACKVAR(-24, 4);
    STACKVAR(-816, 4) = STACKVAR(-36, 4);
    STACKVAR(-812, 4) = STACKVAR(-32, 4);
    STACKVAR(-412, 4) = STACKVAR(-816, 4);
    STACKVAR(-408, 4) = STACKVAR(-812, 4);
    ACCESS(LOCAL(-404), 0, 8) = STACKVAR(-824, 8);
    ACCESS(LOCAL(-396), 0, 8) = unknown_loc_340;
    memcpy(&unknown_loc_6C, LOCAL(-412), 24);
    STACKVAR(-856, 4) = STACKVAR(-20, 4);
    STACKVAR(-852, 4) = STACKVAR(-16, 4);
    double unknown_loc_350 = worldBB.maxCoords.y;
    double unknown_loc_348 = worldBB.maxCoords.x;
    STACKVAR(-436, 8) = unknown_loc_348;
    ACCESS(LOCAL(-428), 0, 8) = unknown_loc_350;
    ACCESS(LOCAL(-420), 0, 8) = STACKVAR(-856, 8);
    memcpy(&unknown_loc_6C.maxCoords, LOCAL(-436), 24);
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[6] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451842;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451815;
    }
    for (unsigned int unknown_loc_35C = 0; unknown_loc_35C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_35C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_35C, 0), 0, 4);
    }
l00451815:
    STACKVAR(-872, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-872, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451842:
    memcpy(&unknown_loc_6C, LOCAL(-36), 24);
    unknown_loc_6C.maxCoords = worldBB.maxCoords;
    unknown_loc_6C.CollectIntersectingSectors(map, *reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)));
    unknown_loc_70->children[7] = BuildNode(*reinterpret_cast<B_PtrArray<B_Sector> *>(LOCAL(-60)), sizeThreshold, unknown_loc_6C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l0045193E;
    }
    if (0x00000000 == 0x00000000)
    {
        goto l00451911;
    }
    for (unsigned int unknown_loc_36C = 0; unknown_loc_36C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_36C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_36C, 0), 0, 4);
    }
l00451911:
    STACKVAR(-888, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-888, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l0045193E:
    B_OctantNodeBase *unknown_loc_1B8 = unknown_loc_70;
    STACKVAR(-60, 4) = GLOBAL(0x005BDB7C);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451A15;
    }
    STACKVAR(-908, 4) = STACKVAR(-40, 4);
    if (STACKVAR(-44, 4) == 0x00000000)
    {
        goto l00451A15;
    }
    if (STACKVAR(-908, 4) == 0x00000000)
    {
        goto l004519E8;
    }
    for (unsigned int unknown_loc_37C = 0; unknown_loc_37C < reinterpret_cast<unsigned int>(STACKVAR(-52, 4)); unknown_loc_37C++)
    {
        delete ACCESS(ARRPTR(STACKVAR(-56, 4), 4, unknown_loc_37C, 0), 0, 4);
    }
l004519E8:
    STACKVAR(-904, 4) = STACKVAR(-56, 4);
    operator delete(STACKVAR(-904, 4));
    STACKVAR(-56, 4) = 0x00000000;
    STACKVAR(-52, 4) = 0x00000000;
    STACKVAR(-44, 4) = 0x00000000;
l00451A15:
    return unknown_loc_1B8;
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
    if (this->m_root != nullptr && -this->m_halfSize * 0.5 - 10.0 < localBB.maxCoords.x && -this->m_halfSize * 0.5 - 10.0 < localBB.maxCoords.y && -this->m_halfSize * 0.5 - 10.0 < localBB.maxCoords.z && this->m_halfSize * 0.5 + 10.0 > localBB.minCoords.x && this->m_halfSize * 0.5 + 10.0 > localBB.minCoords.y && this->m_halfSize * 0.5 + 10.0 > localBB.minCoords.z)
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
            if (-sphere->radius > distance)
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
