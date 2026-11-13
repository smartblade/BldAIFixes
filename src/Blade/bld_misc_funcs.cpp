#include <Control/Events.h>
#include "ProcessorTimer.h"
#include <Sound/Sound.h>
#include <BBLibc/Color.h>
#include <BBLibc/IDataFile.h>
#include <BBLibc/ODataFile.h>
#include "bld_misc_funcs.h"


/*
* Module:                 Blade.exe
* Entry point:            0x0040CF10
*/

const char *ShowInputDialog(HINSTANCE module, HWND window, const char *text)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0040E8E6
*/

int ShowStartupDialog(
    HMODULE module, HWND window, B_YSoundDev *sound, B_Name *rasterName,
    bool showDialog)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00422F3B
*/

void JumpCB(const B_Name &action, float time, float, void *)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0044AD38
*/

light_t * read_light(B_IDataFile *file)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00475B9C
* VC++ mangling:          ??0anim_t@@QAE@XZ
*/

anim_t::anim_t()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00475EEB
* VC++ mangling:          ?AddEvent@anim_t@@QAEXABVB_Name@@M@Z
*/

void anim_t::AddEvent(const B_Name &event_name, float event_frame)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00475F86
* VC++ mangling:          ?DelEvent@anim_t@@QAEXABVB_Name@@@Z
*/

void anim_t::DelEvent(const B_Name &event_name)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00476014
* VC++ mangling:          ?ClearEvents@anim_t@@QAEXXZ
*/

void anim_t::ClearEvents()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00476057
* VC++ mangling:          ?GetEventFrame@anim_t@@QAEMABVB_Name@@@Z
*/

float anim_t::GetEventFrame(const B_Name &event_name)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004760A2
* VC++ mangling:          ??5@YAAAVB_IDataFile@@AAV0@PAVanim_t@@@Z
*/

B_IDataFile &operator >>(B_IDataFile &file, anim_t *anim)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0048DB30
* VC++ mangling:          ??0B_ProcessorTimer@@QAE@XZ
*/

B_ProcessorTimer::B_ProcessorTimer()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x0048DC31
* VC++ mangling:          ?GetTime@B_ProcessorTimer@@QAENXZ
*/

double B_ProcessorTimer::GetTime()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00497AE0
*/

void unknown_00497AE0()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004C21C6
* VC++ mangling:          ??0B_YSoundDev@@QAE@XZ
*/

B_YSoundDev::B_YSoundDev()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004CC8C8
*/

bool GetCurrentDir(char *buffer, int bufferLength)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004F65BE
* VC++ mangling:          ??0B_Combustion@@QAE@ABVB_Name@@0NNNNNN@Z
*/

B_Combustion::B_Combustion(
    const B_Name &object_kind, const B_Name &fire_kind, double upper_treshol,
    double lower_treshold, double flame_height, double flame_size,
    double speed, double livetime)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004F69A4
* VC++ mangling:          ??5@YAAAVB_IDataFile@@AAV0@AAVB_Combustion@@@Z
*/

B_IDataFile& operator >>(B_IDataFile& file, B_Combustion &combustion)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x004F6C54
* VC++ mangling:          ??6@YAAAVB_ODataFile@@AAV0@ABVB_Combustion@@@Z
*/

B_ODataFile& operator <<(B_ODataFile &file, const B_Combustion &combustion)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x00572D73
* VC++ mangling:          ?InsideAA@unknown204@@QAEHH@Z
*/

int unknown204::InsideAA(int AA)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x005AA730
* VC++ mangling:          ?SetTime@B_ProcTexture@@SAXN@Z
*/

void B_ProcTexture::SetTime(double time)
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x005AA881
* VC++ mangling:          ?Update@B_ProcTexture@@QAEXXZ
*/

void B_ProcTexture::Update()
{
}


/*
* Module:                 Blade.exe
* Entry point:            0x005B907E
*/

void InspectBODList()
{
}
#include "CDPlayer.h"
#include <Control/Climbing.h>
