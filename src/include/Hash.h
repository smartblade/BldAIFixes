#ifndef HASH_H

#define HASH_H

template<class T>
class B_Hash
{
public:
    B_Hash()
    {
        size = 0;
        deleteItems = true;
        lastItem = NULL;
    }

    ~B_Hash()
    {
        lastItem = NULL;
        for (int i = 0; i < 256; i++)
        {
            hash[i].Clear(deleteItems);
        }
        size = 0;
    }

    void Add(T *item)
    {
        int hashValue = HashValue(item->Id());
        hash[hashValue].Append(item);
        size++;
    }

    int Remove(const B_Name &key, int deleteItem)
    {
        unsigned int hashValue = HashValue(key);
        int idx = hash[hashValue].FindItemIndex(key);
        if (idx != -1)
        {
            size--;
            if (lastItem != NULL && lastItem->Id() == key)
            {
                lastItem = NULL;
            }
            hash[hashValue].Remove(idx, deleteItem);
            return true;
        }
        return false;
    }

    T *Get(const char *key)
    {
        if (lastItem != NULL && !strcmp(lastItem->Id().String(), key))
            return lastItem;
        int hashValue = HashValue(key);
        int idx = FindItemIndex(hash[hashValue], key);
        if (idx != -1)
        {
            lastItem = hash[hashValue][idx];
            return lastItem;
        }
        return NULL;
    }

    T *Get(unsigned int index)
    {
        if (size <= index)
            return NULL;
        unsigned int numSkipped = 0;
        unsigned int hashValue = 0;
        while ((numSkipped + hash[hashValue].size) <= index)
        {
            numSkipped += hash[hashValue].size;
            hashValue++;
        }
        return hash[hashValue][index - numSkipped];
    }

    int HashValue(const char *key)
    {
        int hashValue = 0;
        while (*key)
        {
            hashValue += *key;
            key++;
        }
        hashValue = hashValue & 0xFF;
        return hashValue;
    }

    unsigned int HashValue(const B_Name &key)
    {
        unsigned int sum = 0;
        int len = key.Length();
        const char *str = key.String();
        for (int i = 0; i < len; i++)
        {
            sum += str[i];
        }
        sum = sum & 0xFF;
        return sum;
    }

    int FindItemIndex(const B_Array<T> &items, const char *key)
    {
         for(unsigned int i = 0; i < items.size; i++)
         {
             const char *itemKey = items.elements[i]->Id().String();
             if (!strcmp(key, itemKey))
                 return i;
         }
         return -1;
    }

    unsigned int Size()
    {
        return size;
    }

    unsigned int size;
    B_PtrArray3<T> hash[256];
    int deleteItems;
    T *lastItem;
};

#endif /* HASH_H */
