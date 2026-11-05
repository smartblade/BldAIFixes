
#ifndef N_DATABASE_H

#define N_DATABASE_H

#include "array.h"
#include "Name.h"
#include "NamedObj.h"
#include <bld_system.h>

#ifdef BBLIBC_LIB_EXPORT
#define BUILD_LIB
#endif
#include <export.h>
#undef BUILD_LIB


struct B_ElementCSV : public B_NamedObj
{
    LIB_EXP virtual ~B_ElementCSV();
    float mass;
    B_Name material;
};


template<class T> class B_NDataBase : public B_PtrArray3<T>
{
};

/* reads the array like operator>> of B_PtrArray, num_alloc is computed with
 * increment first */
template<class TYPE>
B_IDataFile &operator >>(B_IDataFile &file, B_NDataBase<TYPE> &arr)
{
    if (arr.num_alloc != 0)
    {
        arr.Clear(true);
    }
    file >> arr.size;
    arr.num_alloc = ((arr.increment + arr.size - 1) / arr.increment) * arr.increment;
    if (arr.num_alloc != 0)
    {
        arr.elements = new TYPE * [arr.num_alloc];
        for(unsigned int i = 0; i < arr.size; i++)
        {
            arr.elements[i] = new TYPE();
            file >> *arr.elements[i];
        }
    }
    return file;
}

extern LIB_EXP B_NDataBase<B_ElementCSV> B_csvs;

LIB_EXP unsigned int ReadCSV(const char *file_name, B_NDataBase<B_ElementCSV> *csvs);

#endif /* N_DATABASE_H */
