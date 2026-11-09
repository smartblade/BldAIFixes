#ifndef ANIM_H

#define ANIM_H

#include <BBLibc/Name.h>
#include <BBLibc/IDataFile.h>

class anim_t : public B_NamedObj
{
public:
    anim_t();
    void AddEvent(const B_Name &event_name, float event_frame);
    void DelEvent(const B_Name &event_name);
    void ClearEvents();
    float GetEventFrame(const B_Name &event_name);

    /* bases and fields after B_NamedObj (two arrays of events and a field at
     * 0x3C, see the constructor at 0x00475B9C) are not reconstructed yet */
    char unknownFields0C[0x34];
};

B_IDataFile &operator >>(B_IDataFile &file, anim_t *anim);

#endif