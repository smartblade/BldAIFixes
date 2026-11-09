
#ifndef B_BITMAP24_H

#define B_BITMAP24_H

#include <bld_system.h>

#ifdef BBLIBC_LIB_EXPORT
#define BUILD_LIB
#endif
#include <export.h>
#undef BUILD_LIB

/* array of pointers like B_PtrArray without deleteItems */
template<class TYPE>
class B_Array
{
public:
    virtual ~B_Array()
    {
        delete this->elements;
    }

    B_Array(int increment)
    :
        elements(NULL),
        size(0),
        increment(increment),
        num_alloc(0)
    {
    }

    int Append(TYPE *newElement)
    {
        if (num_alloc > size)
        {
            this->elements[size] = newElement;
            size++;
        }
        else
        {
            num_alloc += increment;
            if (size != 0)
            {
                TYPE ** elements = new TYPE *[num_alloc];
                for (unsigned int i = 0; i < size; i++)
                {
                    elements[i] = this->elements[i];
                }
                delete this->elements;
                this->elements = elements;
            }
            else
            {
                this->elements = new TYPE *[num_alloc];
            }
            this->elements[size] = newElement;
            size++;
        }
        return size - 1;
    }

    int Find(TYPE *element)
    {
        for (unsigned int i = 0; i < this->size; i++)
        {
            if (this->elements[i] == element)
            {
                return i;
            }
        }
        return -1;
    }

    void Remove(unsigned int index, int deleteItem)
    {
        if (index >= this->size)
            return;
        if (deleteItem)
        {
            delete this->elements[index];
        }
        if (this->size == 1)
        {
            delete this->elements;
            this->elements = NULL;
            this->size = 0;
            this->num_alloc = 0;
            return;
        }
        if (this->num_alloc >= (this->size + this->increment - 1))
        {
            this->num_alloc -= this->increment;
            TYPE ** elements = new TYPE *[this->num_alloc];
            for (unsigned int i = 0; i < index; i++)
            {
                elements[i] = this->elements[i];
            }
            for (i = index + 1; i < this->size; i++)
            {
                elements[i - 1] = this->elements[i];
            }
            delete this->elements;
            this->elements = elements;
        }
        else
        {
            for (unsigned int i = index + 1; i < this->size; i++)
            {
                this->elements[i - 1] = this->elements[i];
            }
        }
        this->size--;
    }

    TYPE **elements;
    unsigned int size;
    int increment;
    unsigned int num_alloc;
};

class B_BitMap;
class B_Color;
class B_IDataFile;
class B_ODataFile;

class LIB_EXP B_BitMap24
{
public:
    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x10006CB0
    * VC++ mangling:          ??0B_BitMap24@@QAE@HH@Z
    */
    B_BitMap24(int width = 0, int height = 0)
    {
        BitMap24DataList.Append(this);
        this->dimension1 = width;
        this->dimension2 = height;
        if (width != 0 && height != 0)
        {
            this->data = new char[this->dimension1 * this->dimension2 * 3];
        }
        else
        {
            this->data = NULL;
        }
    }

    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x10006E70
    * VC++ mangling:          ??1B_BitMap24@@UAE@XZ
    */
    virtual ~B_BitMap24()
    {
        BitMap24DataList.Remove(BitMap24DataList.Find(this), false);
        if (this->data != NULL)
        {
            delete this->data;
        }
    }

    B_BitMap24(const B_BitMap24 &that);
    static void ClearBitMap24Data();
    B_BitMap24(const B_BitMap &arg_1);
    unsigned int SetBits(int, int, const char*, const char*);
    B_BitMap24 &operator=(const B_BitMap24 &that);
    int SaveToBMP(const char *fileName) const;
    int SaveToBMPSized(const char *fileName, int width, int height) const;
    int ReadFromBMP(const char *arg_1);
    int ReadFromFile(const char *arg_1);
    //B_BitMap24 ReadFromFile(const char*);
    int SaveToFile(const char*, int) const;
    void EscribeArchivoRAW(const char*) const;
    void ChangeRGBOrder();
    unsigned int GetPixelAt(int arg_1, int arg_2, B_Color &arg_3) const;
    //B_BitMap24 ReadFromJPEG(const char*);
    int SaveToJPEG(const char*, int) const;

    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x10006E20
    * VC++ mangling:          ?Clear@B_BitMap24@@QAEXXZ
    */
#ifndef BLD_NATIVE
    void Clear()
    {
    }
#else
    void Clear();
#endif

    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x10007090
    * VC++ mangling:          ?GetDimension@B_BitMap24@@QBEXAAH0@Z
    */
#ifndef BLD_NATIVE
    void GetDimension(int &arg_1, int &arg_2) const
    {
    }
#else
    void GetDimension(int &arg_1, int &arg_2) const;
#endif

    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x100070C0
    * VC++ mangling:          ?GetBits@B_BitMap24@@QBEPBEXZ
    */
#ifndef BLD_NATIVE
    const unsigned char *GetBits() const
    {
        return nullptr;
    }
#else
    const unsigned char *GetBits() const;
#endif

    /*
    *
    * Implicit definition of default constructor closure.
    * Generated by compiler.
    *
    * Module:                 BBLibc.dll
    * Entry point:            0x100070E0
    * VC++ mangling:          ??_FB_BitMap24@@QAEXXZ
    */


    /*
    * Module:                 BBLibc.dll
    * Entry point:            0x10029510
    * VC++ mangling:          ?ReadFromJPEG@B_BitMap24@@QAEHPBD@Z
    */
#ifndef BLD_NATIVE
    int ReadFromJPEG(const char *arg_1)
    {
        return 0;
    }
#else
    int ReadFromJPEG(const char *arg_1);
#endif
    int dimension1;
    int dimension2;
    void *data;
private:
    static B_Array<B_BitMap24> BitMap24DataList;

};

LIB_EXP B_IDataFile &operator >>(B_IDataFile &file, B_BitMap24 &bitMap);
LIB_EXP B_ODataFile &operator <<(B_ODataFile &file, B_BitMap24 const &bitMap);

#endif /* B_BITMAP24_H */
