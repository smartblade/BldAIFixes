#include "RTrisDeviceDLL.h"


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 rOpenGL.dll
* Entry point:            0x1002CA05
* VC++ mangling:          ?unknown0E8@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0E8()
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
* Module:                 rOpenGL.dll
* Entry point:            0x1002E3D1
* VC++ mangling:          ??0B_TrisDevice@@QAE@XZ
*/
#ifndef BLD_NATIVE
B_TrisDevice::B_TrisDevice()
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
* Module:                 rOpenGL.dll
* Entry point:            0x1002EE80
* VC++ mangling:          ?unknown240@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown240()
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
* Module:                 rOpenGL.dll
* Entry point:            0x1002F28D
* VC++ mangling:          ?SetProjection@B_TrisDevice@@UAEXABVB_CameraView@@@Z
*/
#ifndef BLD_NATIVE
void B_TrisDevice::SetProjection(const B_CameraView &cameraView)
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x1002F33F
* VC++ mangling:          ?StartScene@B_TrisDevice@@UAEXPAVB_ViewPose@@@Z
*/

void B_TrisDevice::StartScene(B_ViewPose *cameraPose)
{
    this->unknown007C = false;
    this->unknown07A210 = false;
    this->numVertices = 0;
    this->numEdges = 0;
    this->numTriangles = 0;
    this->numLights = 0;
    this->numPointLights = 0;
    this->redLightIntensity += 2.5;
    if (this->redLightIntensity > 250.0f)
    {
        this->redLightIntensity = 70.0f;
    }
}


/*
* Module:                 rOpenGL.dll
* Entry point:            0x1002F3DF
* VC++ mangling:          ?EndScene@B_TrisDevice@@UAEXXZ
*/

void B_TrisDevice::EndScene()
{
}


/*
* Module:                 rOpenGL.dll
* Entry point:            0x1002F3EA
* VC++ mangling:          ?unknown030@B_TrisDevice@@UAEXXZ
*/

void B_TrisDevice::unknown030()
{
    this->unknown007C = false;
    this->unknown07A210 = false;
}


/*
* Module:                 rOpenGL.dll
* Entry point:            0x1002F40C
* VC++ mangling:          ?unknown034@B_TrisDevice@@UAEXXZ
*/

void B_TrisDevice::unknown034()
{
    this->unknown007C = true;
    this->unknown07A210 = true;
}


/*
................................................................................
................................................................................
................................................................................
................................................................................
*/

/*
* Module:                 rOpenGL.dll
* Entry point:            0x10030E68
* VC++ mangling:          ?unknown0F0@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0F0()
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x10030F8C
* VC++ mangling:          ?unknown244@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown244()
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x100313DE
* VC++ mangling:          ?unknown0F4@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0F4()
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
* Module:                 rOpenGL.dll
* Entry point:            0x100314A0
* VC++ mangling:          ?unknown0BC@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0BC()
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
* Module:                 rOpenGL.dll
* Entry point:            0x10031630
* VC++ mangling:          ?unknown0C4@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0C4()
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
* Module:                 rOpenGL.dll
* Entry point:            0x10031845
* VC++ mangling:          ?unknown0E4@B_TrisDevice@@UAEXXZ
*/
#ifndef BLD_NATIVE
void B_TrisDevice::unknown0E4()
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
* Module:                 rOpenGL.dll
* Entry point:            0x100321A0
* VC++ mangling:          ?SplitEdge@B_TrisDevice@@QAEXPAUB_Edge@@@Z
*/
#ifndef BLD_NATIVE
void B_TrisDevice::SplitEdge(B_Edge *edge)
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x1003248C
* VC++ mangling:          ?SplitLightenedEdges@B_TrisDevice@@QAEHXZ
*/

int B_TrisDevice::SplitLightenedEdges()
{
    float cameraDist = max(
        0.0, this->currentPointLight->pointToPlane.z);
    /* the distance is replaced with the coefficient */
    cameraDist = cameraDist * cameraDist / 1000.0f;
    cameraDist += 30000.0f;
    B_Edge *curEdge = this->edges;
    unsigned int nEdges = this->numEdges;
    unsigned int newEdges = 0;
    float planeCoef =
        this->currentPointLight->planeDist *
        this->currentPointLight->planeDist *
        this->currentPointLight->planeDist * 0.001f;
    for (unsigned int i = 0; i < nEdges; i++)
    {
        if (curEdge->light != this->currentPointLight)
        {
            float minSqrLightDist = min(
                this->vertices[curEdge->firstVertexIndex].sqrLightDist,
                this->vertices[curEdge->secondVertexIndex].sqrLightDist);
            if (
                curEdge->sqrLen >
                    (minSqrLightDist + planeCoef) * 0.3 + cameraDist)
            {
                this->SplitEdge(curEdge);
                newEdges++;
            }
            else
            {
                curEdge->nextEdge = NULL;
                curEdge->light = this->currentPointLight;
            }
        }
        else
        {
            curEdge->nextEdge = NULL;
            curEdge->light = this->currentPointLight;
        }
        curEdge++;
    }
    return newEdges;
}


/*
* Module:                 rOpenGL.dll
* Entry point:            0x10032646
* VC++ mangling:          ?SplitTriangleThreeEdges@B_TrisDevice@@QAEXPAUB_Triangle@@@Z
*/
#ifndef BLD_NATIVE
void B_TrisDevice::SplitTriangleThreeEdges(B_Triangle *triangle)
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x100329C6
* VC++ mangling:          ?SplitTriangleTwoEdges@B_TrisDevice@@QAEXPAUB_Triangle@@@Z
*/
#ifndef BLD_NATIVE
void B_TrisDevice::SplitTriangleTwoEdges(B_Triangle *triangle)
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x10032C9A
* VC++ mangling:          ?SplitTriangleOneEdge@B_TrisDevice@@QAEXPAUB_Triangle@@@Z
*/
#ifndef BLD_NATIVE
void B_TrisDevice::SplitTriangleOneEdge(B_Triangle *triangle)
{
}
#endif

/*
* Module:                 rOpenGL.dll
* Entry point:            0x10032E58
* VC++ mangling:          ?SplitTriangles@B_TrisDevice@@QAEXXZ
*/

void B_TrisDevice::SplitTriangles()
{
    B_Edge *edge;
    int invEdge;
    B_Triangle *tri = this->triangles;
    unsigned int count = this->numTriangles;
    for (unsigned int i = 0; i < count; i++)
    {
        if (tri->edge1->nextEdge != NULL)
        {
            if (tri->edge2->nextEdge != NULL)
            {
                if (tri->edge3->nextEdge != NULL)
                {
                    this->SplitTriangleThreeEdges(tri);
                }
                else
                {
                    this->SplitTriangleTwoEdges(tri);
                }
            }
            else if (tri->edge3->nextEdge != NULL)
            {
                edge = tri->edge1;
                invEdge = tri->invEdge1;
                tri->edge1 = tri->edge3;
                tri->invEdge1 = tri->invEdge3;
                tri->edge3 = tri->edge2;
                tri->invEdge3 = tri->invEdge2;
                tri->edge2 = edge;
                tri->invEdge2 = invEdge;
                this->SplitTriangleTwoEdges(tri);
            }
            else
            {
                this->SplitTriangleOneEdge(tri);
            }
        }
        else if (tri->edge2->nextEdge != NULL)
        {
            if (tri->edge3->nextEdge != NULL)
            {
                edge = tri->edge1;
                invEdge = tri->invEdge1;
                tri->edge1 = tri->edge2;
                tri->invEdge1 = tri->invEdge2;
                tri->edge2 = tri->edge3;
                tri->invEdge2 = tri->invEdge3;
                tri->edge3 = edge;
                tri->invEdge3 = invEdge;
                this->SplitTriangleTwoEdges(tri);
            }
            else
            {
                edge = tri->edge1;
                invEdge = tri->invEdge1;
                tri->edge1 = tri->edge2;
                tri->invEdge1 = tri->invEdge2;
                tri->edge2 = tri->edge3;
                tri->invEdge2 = tri->invEdge3;
                tri->edge3 = edge;
                tri->invEdge3 = invEdge;
                this->SplitTriangleOneEdge(tri);
            }
        }
        else if (tri->edge3->nextEdge != NULL)
        {
            edge = tri->edge1;
            invEdge = tri->invEdge1;
            tri->edge1 = tri->edge3;
            tri->invEdge1 = tri->invEdge3;
            tri->edge3 = tri->edge2;
            tri->invEdge3 = tri->invEdge2;
            tri->edge2 = edge;
            tri->invEdge2 = invEdge;
            this->SplitTriangleOneEdge(tri);
        }
        ++tri;
    }
}
