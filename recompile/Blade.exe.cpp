
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

// address: 0x00404CFD
B_Matrix::B_Matrix(double scale)
{
    DEFINE_MATRIX(
        scale, 0.0, 0.0, 0.0,
        0.0, scale, 0.0, 0.0,
        0.0, 0.0, scale, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
}

// address: 0x00405050
B_Matrix::B_Matrix(const B_Vector &axis, double angle)
{
    double c = cos(angle);
    double s = sin(angle);
    double x = axis.x;
    double y = axis.y;
    double z = axis.z;
    DEFINE_MATRIX(
        x * x * (1.0 - c) + c, x * y * (1.0 - c) + z * s, x * z * (1.0 - c) - y * s, 0.0,
        x * y * (1.0 - c) - z * s, y * y + (x * x + z * z) * c, y * z * (1.0 - c) + x * s, 0.0,
        x * z * (1.0 - c) + y * s, y * z * (1.0 - c) - x * s, z * z * (1.0 - c) + c, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
}

// address: 0x00405227
B_Matrix::B_Matrix(const B_Plane &plane)
{
    this->m[0][0] = 1.0 - 2.0 * plane.normal.x * plane.normal.x;
    this->m[1][0] = -2.0 * plane.normal.x * plane.normal.y;
    this->m[2][0] = -2.0 * plane.normal.x * plane.normal.z;
    this->m[3][0] = -2.0 * plane.normal.x * plane.p;
    this->m[0][1] = -2.0 * plane.normal.y * plane.normal.x;
    this->m[1][1] = 1.0 - 2.0 * plane.normal.y * plane.normal.y;
    this->m[2][1] = -2.0 * plane.normal.y * plane.normal.z;
    this->m[3][1] = -2.0 * plane.normal.y * plane.p;
    this->m[0][2] = -2.0 * plane.normal.z * plane.normal.x;
    this->m[1][2] = -2.0 * plane.normal.z * plane.normal.y;
    this->m[2][2] = 1.0 - 2.0 * plane.normal.z * plane.normal.z;
    this->m[3][2] = -2.0 * plane.normal.z * plane.p;
    this->m[0][3] = 0.0;
    this->m[1][3] = 0.0;
    this->m[2][3] = 0.0;
    this->m[3][3] = 1.0;
}

// address: 0x0040578A
void B_Matrix::SetOrigin(const B_Vector *origin)
{
    this->m[3][0] = origin->x;
    this->m[3][1] = origin->y;
    this->m[3][2] = origin->z;
}

// address: 0x004057CC
double B_Matrix::ScaleX() const
{
    return sqrt(this->m[0][0] * this->m[0][0] + this->m[0][1] * this->m[0][1] + this->m[0][2] * this->m[0][2]);
}

// address: 0x00405802
double B_Matrix::ScaleY() const
{
    return sqrt(this->m[1][0] * this->m[1][0] + this->m[1][1] * this->m[1][1] + this->m[1][2] * this->m[1][2]);
}

// address: 0x0040583A
double B_Matrix::ScaleZ() const
{
    return sqrt(this->m[2][0] * this->m[2][0] + this->m[2][1] * this->m[2][1] + this->m[2][2] * this->m[2][2]);
}

// address: 0x00405872
void B_Matrix::SetScale(double scale)
{
    double lenX = this->ScaleX();
    double lenY = this->ScaleY();
    double lenZ = this->ScaleZ();
    double kX = scale / lenX;
    double kY = scale / lenY;
    double kZ = scale / lenZ;
    this->m[0][0] = kX * this->m[0][0];
    this->m[0][1] = kX * this->m[0][1];
    this->m[0][2] = kX * this->m[0][2];
    this->m[1][0] = kY * this->m[1][0];
    this->m[1][1] = kY * this->m[1][1];
    this->m[1][2] = kY * this->m[1][2];
    this->m[2][0] = kZ * this->m[2][0];
    this->m[2][1] = kZ * this->m[2][1];
    this->m[2][2] = kZ * this->m[2][2];
}

// address: 0x004059EF
void B_Matrix::RemoveScale()
{
    double lenX = this->ScaleX();
    double lenY = this->ScaleY();
    double lenZ = this->ScaleZ();
    this->m[0][0] /= lenX;
    this->m[0][1] /= lenX;
    this->m[0][2] /= lenX;
    this->m[1][0] /= lenY;
    this->m[1][1] /= lenY;
    this->m[1][2] /= lenY;
    this->m[2][0] /= lenZ;
    this->m[2][1] /= lenZ;
    this->m[2][2] /= lenZ;
}

// address: 0x00405AA2
void B_Matrix::InvertRigid(B_Matrix &out)
{
    for (unsigned int i = 0; i < 3; i++)
    {
        for (unsigned int j = 0; j < 3; j++)
        {
            out.m[i][j] = this->m[j][i];
        }
    }
    B_Vector translation(this->m[3][0], this->m[3][1], this->m[3][2]);
    translation = Rotate(translation, out);
    out.m[3][0] = -translation.x;
    out.m[3][1] = -translation.y;
    out.m[3][2] = -translation.z;
}

// address: 0x00405BA9
B_Matrix B_Matrix::Invert() const
{
    B_Matrix temp;
    double det = this->m[0][0] * this->m[1][1] * this->m[2][2] + this->m[0][1] * this->m[1][2] * this->m[2][0] + this->m[1][0] * this->m[2][1] * this->m[0][2] - this->m[0][2] * this->m[1][1] * this->m[2][0] - this->m[0][1] * this->m[1][0] * this->m[2][2] - this->m[1][2] * this->m[2][1] * this->m[0][0];
    temp.m[0][0] = (this->m[1][1] * this->m[2][2] - this->m[1][2] * this->m[2][1]) / det;
    temp.m[1][0] = -(this->m[1][0] * this->m[2][2] - this->m[1][2] * this->m[2][0]) / det;
    temp.m[2][0] = (this->m[1][0] * this->m[2][1] - this->m[1][1] * this->m[2][0]) / det;
    temp.m[0][1] = -(this->m[0][1] * this->m[2][2] - this->m[0][2] * this->m[2][1]) / det;
    temp.m[1][1] = (this->m[0][0] * this->m[2][2] - this->m[0][2] * this->m[2][0]) / det;
    temp.m[2][1] = -(this->m[0][0] * this->m[2][1] - this->m[0][1] * this->m[2][0]) / det;
    temp.m[0][2] = (this->m[0][1] * this->m[1][2] - this->m[0][2] * this->m[1][1]) / det;
    temp.m[1][2] = -(this->m[0][0] * this->m[1][2] - this->m[0][2] * this->m[1][0]) / det;
    temp.m[2][2] = (this->m[0][0] * this->m[1][1] - this->m[0][1] * this->m[1][0]) / det;
    B_Vector translation(this->m[3][0], this->m[3][1], this->m[3][2]);
    translation = Rotate(translation, temp);
    temp.m[3][0] = -translation.x;
    temp.m[3][1] = -translation.y;
    temp.m[3][2] = -translation.z;
    return temp;
}

// address: 0x00405F0D
int operator ==(const B_Matrix &a, const B_Matrix &b)
{
    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            if (fabs(a.m[i][j] - b.m[i][j]) > 0.001)
            {
                return 0;
            }
        }
    }
    return 1;
}

// address: 0x00405F87
B_Matrix operator *(const B_Matrix &a, const B_Matrix &b)
{
    B_Matrix result;
    result.m[0][0] = a.m[0][0] * b.m[0][0] + a.m[0][1] * b.m[1][0] + a.m[0][2] * b.m[2][0] + a.m[0][3] * b.m[3][0];
    result.m[0][1] = a.m[0][0] * b.m[0][1] + a.m[0][1] * b.m[1][1] + a.m[0][2] * b.m[2][1] + a.m[0][3] * b.m[3][1];
    result.m[0][2] = a.m[0][0] * b.m[0][2] + a.m[0][1] * b.m[1][2] + a.m[0][2] * b.m[2][2] + a.m[0][3] * b.m[3][2];
    result.m[0][3] = a.m[0][0] * b.m[0][3] + a.m[0][1] * b.m[1][3] + a.m[0][2] * b.m[2][3] + a.m[0][3] * b.m[3][3];
    result.m[1][0] = a.m[1][0] * b.m[0][0] + a.m[1][1] * b.m[1][0] + a.m[1][2] * b.m[2][0] + a.m[1][3] * b.m[3][0];
    result.m[1][1] = a.m[1][0] * b.m[0][1] + a.m[1][1] * b.m[1][1] + a.m[1][2] * b.m[2][1] + a.m[1][3] * b.m[3][1];
    result.m[1][2] = a.m[1][0] * b.m[0][2] + a.m[1][1] * b.m[1][2] + a.m[1][2] * b.m[2][2] + a.m[1][3] * b.m[3][2];
    result.m[1][3] = a.m[1][0] * b.m[0][3] + a.m[1][1] * b.m[1][3] + a.m[1][2] * b.m[2][3] + a.m[1][3] * b.m[3][3];
    result.m[2][0] = a.m[2][0] * b.m[0][0] + a.m[2][1] * b.m[1][0] + a.m[2][2] * b.m[2][0] + a.m[2][3] * b.m[3][0];
    result.m[2][1] = a.m[2][0] * b.m[0][1] + a.m[2][1] * b.m[1][1] + a.m[2][2] * b.m[2][1] + a.m[2][3] * b.m[3][1];
    result.m[2][2] = a.m[2][0] * b.m[0][2] + a.m[2][1] * b.m[1][2] + a.m[2][2] * b.m[2][2] + a.m[2][3] * b.m[3][2];
    result.m[2][3] = a.m[2][0] * b.m[0][3] + a.m[2][1] * b.m[1][3] + a.m[2][2] * b.m[2][3] + a.m[2][3] * b.m[3][3];
    result.m[3][0] = a.m[3][0] * b.m[0][0] + a.m[3][1] * b.m[1][0] + a.m[3][2] * b.m[2][0] + a.m[3][3] * b.m[3][0];
    result.m[3][1] = a.m[3][0] * b.m[0][1] + a.m[3][1] * b.m[1][1] + a.m[3][2] * b.m[2][1] + a.m[3][3] * b.m[3][1];
    result.m[3][2] = a.m[3][0] * b.m[0][2] + a.m[3][1] * b.m[1][2] + a.m[3][2] * b.m[2][2] + a.m[3][3] * b.m[3][2];
    result.m[3][3] = a.m[3][0] * b.m[0][3] + a.m[3][1] * b.m[1][3] + a.m[3][2] * b.m[2][3] + a.m[3][3] * b.m[3][3];
    return result;
}

// address: 0x00406338
B_Matrix MulRot_406338(const B_Matrix &a, const B_Matrix &b)
{
    B_Matrix result;
    result.m[0][0] = a.m[0][0] * b.m[0][0] + a.m[0][1] * b.m[1][0] + a.m[0][2] * b.m[2][0];
    result.m[0][1] = a.m[0][0] * b.m[0][1] + a.m[0][1] * b.m[1][1] + a.m[0][2] * b.m[2][1];
    result.m[0][2] = a.m[0][0] * b.m[0][2] + a.m[0][1] * b.m[1][2] + a.m[0][2] * b.m[2][2];
    result.m[0][3] = a.m[0][3];
    result.m[1][0] = a.m[1][0] * b.m[0][0] + a.m[1][1] * b.m[1][0] + a.m[1][2] * b.m[2][0];
    result.m[1][1] = a.m[1][0] * b.m[0][1] + a.m[1][1] * b.m[1][1] + a.m[1][2] * b.m[2][1];
    result.m[1][2] = a.m[1][0] * b.m[0][2] + a.m[1][1] * b.m[1][2] + a.m[1][2] * b.m[2][2];
    result.m[1][3] = a.m[1][3];
    result.m[2][0] = a.m[2][0] * b.m[0][0] + a.m[2][1] * b.m[1][0] + a.m[2][2] * b.m[2][0];
    result.m[2][1] = a.m[2][0] * b.m[0][1] + a.m[2][1] * b.m[1][1] + a.m[2][2] * b.m[2][1];
    result.m[2][2] = a.m[2][0] * b.m[0][2] + a.m[2][1] * b.m[1][2] + a.m[2][2] * b.m[2][2];
    result.m[2][3] = a.m[2][3];
    result.m[3][0] = a.m[3][0];
    result.m[3][1] = a.m[3][1];
    result.m[3][2] = a.m[3][2];
    result.m[3][3] = a.m[3][3];
    return result;
}

// address: 0x00406547
void MatrixMultiply(B_Matrix *out, const B_Matrix *a, const B_Matrix *b)
{
    out->m[0][0] = a->m[0][0] * b->m[0][0] + a->m[0][1] * b->m[1][0] + a->m[0][2] * b->m[2][0] + a->m[0][3] * b->m[3][0];
    out->m[0][1] = a->m[0][0] * b->m[0][1] + a->m[0][1] * b->m[1][1] + a->m[0][2] * b->m[2][1] + a->m[0][3] * b->m[3][1];
    out->m[0][2] = a->m[0][0] * b->m[0][2] + a->m[0][1] * b->m[1][2] + a->m[0][2] * b->m[2][2] + a->m[0][3] * b->m[3][2];
    out->m[0][3] = a->m[0][0] * b->m[0][3] + a->m[0][1] * b->m[1][3] + a->m[0][2] * b->m[2][3] + a->m[0][3] * b->m[3][3];
    out->m[1][0] = a->m[1][0] * b->m[0][0] + a->m[1][1] * b->m[1][0] + a->m[1][2] * b->m[2][0] + a->m[1][3] * b->m[3][0];
    out->m[1][1] = a->m[1][0] * b->m[0][1] + a->m[1][1] * b->m[1][1] + a->m[1][2] * b->m[2][1] + a->m[1][3] * b->m[3][1];
    out->m[1][2] = a->m[1][0] * b->m[0][2] + a->m[1][1] * b->m[1][2] + a->m[1][2] * b->m[2][2] + a->m[1][3] * b->m[3][2];
    out->m[1][3] = a->m[1][0] * b->m[0][3] + a->m[1][1] * b->m[1][3] + a->m[1][2] * b->m[2][3] + a->m[1][3] * b->m[3][3];
    out->m[2][0] = a->m[2][0] * b->m[0][0] + a->m[2][1] * b->m[1][0] + a->m[2][2] * b->m[2][0] + a->m[2][3] * b->m[3][0];
    out->m[2][1] = a->m[2][0] * b->m[0][1] + a->m[2][1] * b->m[1][1] + a->m[2][2] * b->m[2][1] + a->m[2][3] * b->m[3][1];
    out->m[2][2] = a->m[2][0] * b->m[0][2] + a->m[2][1] * b->m[1][2] + a->m[2][2] * b->m[2][2] + a->m[2][3] * b->m[3][2];
    out->m[2][3] = a->m[2][0] * b->m[0][3] + a->m[2][1] * b->m[1][3] + a->m[2][2] * b->m[2][3] + a->m[2][3] * b->m[3][3];
    out->m[3][0] = a->m[3][0] * b->m[0][0] + a->m[3][1] * b->m[1][0] + a->m[3][2] * b->m[2][0] + a->m[3][3] * b->m[3][0];
    out->m[3][1] = a->m[3][0] * b->m[0][1] + a->m[3][1] * b->m[1][1] + a->m[3][2] * b->m[2][1] + a->m[3][3] * b->m[3][1];
    out->m[3][2] = a->m[3][0] * b->m[0][2] + a->m[3][1] * b->m[1][2] + a->m[3][2] * b->m[2][2] + a->m[3][3] * b->m[3][2];
    out->m[3][3] = a->m[3][0] * b->m[0][3] + a->m[3][1] * b->m[1][3] + a->m[3][2] * b->m[2][3] + a->m[3][3] * b->m[3][3];
}

// address: 0x00406903
B_Vector operator *(const B_Vector &vector, const B_Matrix &matrix)
{
    return B_Vector(vector.x * matrix.m[0][0] + vector.y * matrix.m[1][0] + vector.z * matrix.m[2][0] + matrix.m[3][0], vector.x * matrix.m[0][1] + vector.y * matrix.m[1][1] + vector.z * matrix.m[2][1] + matrix.m[3][1], vector.x * matrix.m[0][2] + vector.y * matrix.m[1][2] + vector.z * matrix.m[2][2] + matrix.m[3][2]);
}

// address: 0x004069CB
void TransformPoint(B_Vector &out, const B_Vector &v, const B_Matrix &matrix)
{
    out.x = v.x * matrix.m[0][0] + v.y * matrix.m[1][0] + v.z * matrix.m[2][0] + matrix.m[3][0];
    out.y = v.x * matrix.m[0][1] + v.y * matrix.m[1][1] + v.z * matrix.m[2][1] + matrix.m[3][1];
    out.z = v.x * matrix.m[0][2] + v.y * matrix.m[1][2] + v.z * matrix.m[2][2] + matrix.m[3][2];
}

// address: 0x00406A67
void Rotate(B_Vector &out, const B_Vector &v, const B_Matrix &rotateMatrix)
{
    out.x = v.x * rotateMatrix.m[0][0] + v.y * rotateMatrix.m[1][0] + v.z * rotateMatrix.m[2][0];
    out.y = v.x * rotateMatrix.m[0][1] + v.y * rotateMatrix.m[1][1] + v.z * rotateMatrix.m[2][1];
    out.z = v.x * rotateMatrix.m[0][2] + v.y * rotateMatrix.m[1][2] + v.z * rotateMatrix.m[2][2];
}

// address: 0x00406AF1
B_Vector Rotate(const B_Vector &v, const B_Matrix &rotateMatrix)
{
    return B_Vector(v.x * rotateMatrix.m[0][0] + v.y * rotateMatrix.m[1][0] + v.z * rotateMatrix.m[2][0], v.x * rotateMatrix.m[0][1] + v.y * rotateMatrix.m[1][1] + v.z * rotateMatrix.m[2][1], v.x * rotateMatrix.m[0][2] + v.y * rotateMatrix.m[1][2] + v.z * rotateMatrix.m[2][2]);
}

// address: 0x00406BA7
void TransformPlane(B_Plane &out, const B_Plane &in, const B_Matrix &matrix)
{
    out.normal.x = in.normal.x * matrix.m[0][0] + in.normal.y * matrix.m[1][0] + in.normal.z * matrix.m[2][0];
    out.normal.y = in.normal.x * matrix.m[0][1] + in.normal.y * matrix.m[1][1] + in.normal.z * matrix.m[2][1];
    out.normal.z = in.normal.x * matrix.m[0][2] + in.normal.y * matrix.m[1][2] + in.normal.z * matrix.m[2][2];
    out.p = in.p - out.normal.x * matrix.m[3][0] - out.normal.y * matrix.m[3][1] - out.normal.z * matrix.m[3][2];
}

// address: 0x00406C69
B_IDataFile &operator >>(B_IDataFile &file, B_Matrix &matrix)
{
    file.Read(&matrix, sizeof(B_Matrix));
    return file;
}

// address: 0x00406C83
B_ODataFile &operator <<(B_ODataFile &file, const B_Matrix &matrix)
{
    file.Write(&matrix, sizeof(B_Matrix));
    return file;
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
    double max_x;
    double min_x;
    double max_y;
    double min_y;
    double max_z;
    double min_z;
    if (this->m_root != nullptr)
    {
        delete this->m_root;
    }
    this->m_halfSize = 0.0;
    B_BoundingBox worldBB;
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
        this->m_halfSize = max(max_x - min_x, max(max_y - min_y, max_z - min_z)) + 2.0 * minNodeSize;
        this->m_center.x = (max_x + min_x) * 0.5;
        this->m_center.y = (max_y + min_y) * 0.5;
        this->m_center.z = (max_z + min_z) * 0.5;
        worldBB.minCoords = this->m_center - 0.5 * B_Vector(this->m_halfSize, this->m_halfSize, this->m_halfSize);
        worldBB.maxCoords = this->m_center + 0.5 * B_Vector(this->m_halfSize, this->m_halfSize, this->m_halfSize);
    }
    this->m_root = BuildNode(map, minNodeSize, worldBB);
    mout << vararg("OctTree with %d nodes.\n", gbl_node_count);
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
