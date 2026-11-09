#ifndef ATMOSPHERE_H

#define ATMOSPHERE_H

#include <BBLibc/Color.h>
#include <BBLibc/NamedObj.h>
#include <BBLibc/IDataFile.h>
#include <array.h>

class atmosphere_t : public B_NamedObj
{
public:
        atmosphere_t();
public:
        B_Color color;
        float intensity;
};

B_IDataFile &operator >>(B_IDataFile &file, atmosphere_t *atm);

/* like operator >> of B_Array, the atmospheres are read by pointers */
inline B_IDataFile &operator >>(
    B_IDataFile &file, B_DataBase<atmosphere_t> &atmospheres)
{
    if (atmospheres.num_alloc != 0)
    {
        atmospheres.Clear(true);
    }
    file >> atmospheres.size;
    atmospheres.num_alloc =
        ((atmospheres.size + atmospheres.increment - 1) /
         atmospheres.increment) * atmospheres.increment;
    if (atmospheres.num_alloc != 0)
    {
        atmospheres.elements = new atmosphere_t *[atmospheres.num_alloc];
        for (unsigned int i = 0; i < atmospheres.size; i++)
        {
            atmospheres.elements[i] = new atmosphere_t();
            file >> atmospheres.elements[i];
        }
    }
    return file;
}

#endif /* ATMOSPHERE_H */
