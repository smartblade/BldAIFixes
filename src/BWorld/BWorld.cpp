
#include <bld_system.h>
#include <Raster/RasterDevice.h>
#include <BWorld/BWorld.h>
#include <BWorld/BMap.h>
#include <BWorld/light.h>
#include "bld_misc_funcs.h"


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x00439F5D
* VC++ mangling:          ?unknown_00439F5D@B_World@@QAEXXZ
*/

#ifndef BLD_NATIVE

void B_World::unknown_00439F5D()
{
}

#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x0043A6A4
* VC++ mangling:          ?GetTime@B_World@@QAENXZ
*/
#ifndef BLD_NATIVE
double B_World::GetTime()
{
    return 0.0;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043A6B8
* VC++ mangling:          ?SetTime@B_World@@QAEHN@Z
*/
#ifndef BLD_NATIVE
int B_World::SetTime(double time)
{
    return true;
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x0043AC07
* VC++ mangling:          ?GoToTime@B_World@@QAEXN@Z
*/
#ifndef BLD_NATIVE
void B_World::GoToTime(double time)
{
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x0043B8E6
* VC++ mangling:          ?AddScheduledFunc@B_World@@QAEXNPAUPyObject@@0PBD@Z
*/
#ifndef BLD_NATIVE
void B_World::AddScheduledFunc(
    double time, PyObject *func, PyObject *args, const char *name)
{
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x0043C5FD
* VC++ mangling:          ?Update@B_World@@QAEXPAVB_ViewPose@@PAXNH@Z
*/
#ifndef BLD_NATIVE
void B_World::Update(
    B_ViewPose *viewPose, void *cameraView, double time, int updateRaster)
{
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043C8B2
* VC++ mangling:          ?SetSun@B_World@@QAEXHABVB_Vector@@@Z
*/

#ifndef BLD_NATIVE

void B_World::SetSun(int exists, const B_Vector &position)
{
}

#endif


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x0043D434
* VC++ mangling:          ?GetEnemiesVisibleFrom@B_World@@QAEXABVB_Vector@@N0NPAV?$B_PtrArray@VB_Entity@@@@@Z
*/
#ifndef BLD_NATIVE
void B_World::GetEnemiesVisibleFrom(
    const B_Vector &position, double radius,
    const B_Vector &direction, double angle, B_PtrArray<B_Entity> *enemies)
{
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x0043DBBE
* VC++ mangling:          ?FindSectorIndex@B_World@@QAEHABVB_Vector@@@Z
*/

#ifndef BLD_NATIVE

int B_World::FindSectorIndex(const B_Vector &point)
{
    return -1;
}

#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043DC20
* VC++ mangling:          ?IntersectSegment@B_World@@QAEHABVB_Vector@@00HHPAX@Z
*/
#ifndef BLD_NATIVE
int B_World::IntersectSegment(
    const B_Vector &startPoint, const B_Vector &endPoint,
    const B_Vector &intersection, int flags, int, void *)
{
    return 0;
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x0043E8E8
* VC++ mangling:          ?GenerateEntityName@B_World@@QAEPBDPBD@Z
*/
#ifndef BLD_NATIVE
const char *B_World::GenerateEntityName(const char *prefix)
{
    return NULL;
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x0043EF43
* VC++ mangling:          ?SetTriggerSectorFunc@B_World@@QAEHPBD0PAUPyObject@@@Z
*/
#ifndef BLD_NATIVE
int B_World::SetTriggerSectorFunc(
    const char *trigger_sector_name, const char *func_type,
    PyObject *func
)
{
    return 0;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F172
* VC++ mangling:          ?GetTriggerSectorFloorHeight@B_World@@QAEHPBD@Z
*/
#ifndef BLD_NATIVE
int B_World::GetTriggerSectorFloorHeight(const char *trigger_sector_name)
{
    return 0;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F209
* VC++ mangling:          ?GetTriggerSectorRoofHeight@B_World@@QAEHPBD@Z
*/
#ifndef BLD_NATIVE
int B_World::GetTriggerSectorRoofHeight(const char *trigger_sector_name)
{
    return 0;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F2A0
* VC++ mangling:          ?GetTriggerSectorGroup@B_World@@QAEPBDPBD@Z
*/
#ifndef BLD_NATIVE
const char *B_World::GetTriggerSectorGroup(const char *trigger_sector_name)
{
    return NULL;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F332
* VC++ mangling:          ?GetTriggerSectorPoints@B_World@@QAEPANPBD@Z
*/
#ifndef BLD_NATIVE
double *B_World::GetTriggerSectorPoints(const char *trigger_sector_name)
{
    return NULL;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F467
* VC++ mangling:          ?GetTriggerSectorFunc@B_World@@QAEPAUPyObject@@PBD0@Z
*/
#ifndef BLD_NATIVE
PyObject *B_World::GetTriggerSectorFunc(
    const char *trigger_sector_name, const char *func_type
)
{
    return NULL;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F56D
* VC++ mangling:          ?SetTriggerSectorData@B_World@@QAEHPBDPAUPyObject@@@Z
*/
#ifndef BLD_NATIVE
int B_World::SetTriggerSectorData(
    const char *trigger_sector_name, PyObject *data
)
{
    return 0;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043F65D
* VC++ mangling:          ?GetTriggerSectorData@B_World@@QAEPAUPyObject@@PBD@Z
*/
#ifndef BLD_NATIVE
PyObject *B_World::GetTriggerSectorData(const char *trigger_sector_name)
{
    return NULL;
}
#endif


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x000043F98A
* VC++ mangling:          ?LoadEntitiesData@B_World@@QAEHPBD@Z
*/

#ifndef BLD_NATIVE

int B_World::LoadEntitiesData(const char *filename)
{
    return 0;
}

#endif

/*
* Module:                 Blade.exe
* Entry point:            0x0043FD82
* VC++ mangling:          ?SaveEntitiesData@B_World@@QAEHPBD@Z
*/

#ifndef BLD_NATIVE

int B_World::SaveEntitiesData(const char *filename)
{
    return 0;
}

#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 Blade.exe
* Entry point:            0x0044008F
* VC++ mangling:          ?AddPoint@B_TriggerSector@@QAEXABVB_Vector@@H@Z
*/
#ifndef BLD_NATIVE
void B_TriggerSector::AddPoint(const B_Vector& point, int numPoints)
{
}
#endif

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/


/*
* Module:                 Blade.exe
* Entry point:            0x00440A19
* VC++ mangling:          ?GetTriggerSectorName@B_World@@QAEPBDH@Z
*/
#ifndef BLD_NATIVE
const char *B_World::GetTriggerSectorName(int index)
{
    return NULL;
}
#endif

/*
* Module:                 Blade.exe
* Entry point:            0x00440A5D
* VC++ mangling:          ??5@YAAAVB_IDataFile@@AAV0@PAVB_World@@@Z
*/

B_IDataFile& operator >>(B_IDataFile& file, B_World *world)
{
        unsigned int num_lights;
        unsigned int i;

        world->lastTime = 0;
        file >> world->atmospheres;

        if (B_3D_raster_device)
                B_3D_raster_device->unknown084();

        for(i = 0; i < world->atmospheres.size; i++)
        {
                atmosphere_t *atm = world->atmospheres.elements[i];
                B_3D_raster_device->AddAtmosphere(atm->Id(), atm->color, atm->intensity);
        }

        file >> gbl_world_points;
        file >> world->map;

        world->lights.Clear(true);

        file >> num_lights;

        for(i = 0; i < num_lights; i++)
        {
                world->lights.Append(read_light(&file));
        }

        for(i = 0; i < num_lights; i++)
        {
                world->lights[i]->unknown008();
        }

        file >> world->initial_point_position >> world->initial_point_orientation;

        for(i = 0; i < world->map.size; i++)
        {
                file >> world->map.elements[i]->groupId;
        }

        world->octTree.Build(world->map, 5000.0);

        return file;
}

/*
................................................................................
................................................................................
................................................................................
................................................................................
*/
