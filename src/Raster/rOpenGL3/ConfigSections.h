#pragma once

#include "GLVideoMode.h"
#include <BBLibc/Name.h>


class B_ConfigSection
{
public:
    B_ConfigSection(const B_Name &fileName, const B_Name &sectionName)
        : fileName(fileName), sectionName(sectionName)
    {
    }

    virtual int Read()
    {
        return 0;
    }

    virtual int Write()
    {
        return 0;
    }

    virtual int unknown008()
    {
        return 0;
    }

private:
    B_Name fileName;
    B_Name sectionName;
};

class B_VideoModeSection : public B_ConfigSection
{
public:
    B_VideoModeSection(const char *fileName)
        : B_ConfigSection(fileName, "VideoModes")
    {
        GetVideoModes(this->videoModes);
        Read();
    }

    virtual int Read();
    virtual int Write();

    virtual int unknown008()
    {
        return 0;
    }

    int isWindow;
    int bpp;
    int width;
    int height;
    int flags;
    int frequency;
    B_Array<B_VideoMode> videoModes;
};
