#include <AnalyticGeometry/Vector.h>
#include <BBLibc/IDataFile.h>

class B_Plane
{
public:
    virtual ~B_Plane()
    {
    }

    double Distance(const B_Vector *point) const
    {
        return this->p + (
            point->x * this->normal.x +
            point->y * this->normal.y +
            point->z * this->normal.z
        );
    }

    B_Vector normal;
    double p;
};
