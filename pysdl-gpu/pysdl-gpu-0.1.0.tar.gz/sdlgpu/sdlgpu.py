# Copyright (c) 2018 Jjp137
# Licensed under the terms of the MIT License

from ctypes import (CFUNCTYPE, POINTER, Structure, c_float, c_int, c_uint,
                    c_ubyte, c_ushort, c_char_p, c_void_p)
import os

from sdl2.dll import DLL
from sdl2.pixels import SDL_Color
from sdl2.rwops import SDL_RWops
from sdl2.stdinc import Sint16, Uint8, Uint16, Uint32
from sdl2.surface import SDL_Surface
from sdl2.version import SDL_version

__all__ = ["SDL_GPU_VERSION_MAJOR", "SDL_GPU_VERSION_MINOR",
           "SDL_GPU_VERSION_PATCH", "GPU_bool", "GPU_FALSE", "GPU_TRUE",
           "GPU_Rect", "GPU_RENDERER_ORDER_MAX", "GPU_RendererEnum",
           "GPU_RENDERER_UNKNOWN", "GPU_RENDERER_OPENGL_1_BASE",
           "GPU_RENDERER_OPENGL_1", "GPU_RENDERER_OPENGL_2",
           "GPU_RENDERER_OPENGL_3","GPU_RENDERER_OPENGL_4",
           "GPU_RENDERER_GLES_1", "GPU_RENDERER_GLES_2", "GPU_RENDERER_GLES_3",
           "GPU_RENDERER_D3D9", "GPU_RENDERER_D3D10", "GPU_RENDERER_D3D11",
           "GPU_RendererID", "GPU_BlendFuncEnum", "GPU_FUNC_ZERO",
           "GPU_FUNC_ONE", "GPU_FUNC_SRC_COLOR", "GPU_FUNC_DST_COLOR",
           "GPU_FUNC_ONE_MINUS_SRC", "GPU_FUNC_ONE_MINUS_DST",
           "GPU_FUNC_SRC_ALPHA", "GPU_FUNC_DST_ALPHA",
           "GPU_FUNC_ONE_MINUS_SRC_ALPHA", "GPU_FUNC_ONE_MINUS_DST_ALPHA",
           "GPU_BlendEqEnum", "GPU_EQ_ADD", "GPU_EQ_SUBTRACT",
           "GPU_EQ_REVERSE_SUBTRACT", "GPU_BlendMode", "GPU_BlendPresetEnum",
           "GPU_BLEND_NORMAL", "GPU_BLEND_PREMULTIPLIED_ALPHA",
           "GPU_BLEND_MULTIPLY", "GPU_BLEND_ADD", "GPU_BLEND_SUBTRACT",
           "GPU_BLEND_MOD_ALPHA", "GPU_BLEND_SET_ALPHA",
           "GPU_BLEND_SET", "GPU_BLEND_NORMAL_KEEP_ALPHA",
           "GPU_BLEND_NORMAL_ADD_ALPHA", "GPU_BLEND_NORMAL_FACTOR_ALPHA",
           "GPU_FilterEnum", "GPU_FILTER_NEAREST", "GPU_FILTER_LINEAR",
           "GPU_FILTER_LINEAR_MIPMAP", "GPU_SnapEnum", "GPU_SNAP_NONE",
           "GPU_SNAP_POSITION", "GPU_SNAP_DIMENSIONS",
           "GPU_SNAP_POSITION_AND_DIMENSIONS", "GPU_WrapEnum",
           "GPU_WRAP_NONE", "GPU_WRAP_REPEAT", "GPU_WRAP_MIRRORED",
           "GPU_FormatEnum", "GPU_FORMAT_LUMINANCE",
           "GPU_FORMAT_LUMINANCE_ALPHA", "GPU_FORMAT_RGB",
           "GPU_FORMAT_RGBA", "GPU_FORMAT_ALPHA", "GPU_FORMAT_RG",
           "GPU_FORMAT_YCbCr422", "GPU_FORMAT_YCbCr420P",
           "GPU_FORMAT_BGR", "GPU_FORMAT_BGRA", "GPU_FORMAT_ABGR",
           "GPU_FileFormatEnum", "GPU_FILE_AUTO", "GPU_FILE_PNG",
           "GPU_FILE_BMP", "GPU_FILE_TGA", "GPU_Image", "GPU_Camera",
           "GPU_ShaderBlock", "GPU_MODELVIEW", "GPU_PROJECTION",
           "GPU_MatrixStack", "GPU_Context", "GPU_Target", "GPU_FeatureEnum",
           "GPU_FEATURE_NON_POWER_OF_TWO", "GPU_FEATURE_RENDER_TARGETS",
           "GPU_FEATURE_BLEND_EQUATIONS", "GPU_FEATURE_BLEND_FUNC_SEPARATE",
           "GPU_FEATURE_BLEND_EQUATIONS_SEPARATE", "GPU_FEATURE_GL_BGR",
           "GPU_FEATURE_GL_BGRA", "GPU_FEATURE_GL_ABGR",
           "GPU_FEATURE_VERTEX_SHADER", "GPU_FEATURE_FRAGMENT_SHADER",
           "GPU_FEATURE_PIXEL_SHADER", "GPU_FEATURE_GEOMETRY_SHADER",
           "GPU_FEATURE_WRAP_REPEAT_MIRRORED",
           "GPU_FEATURE_CORE_FRAMEBUFFER_OBJECTS",
           "GPU_FEATURE_ALL_BASE", "GPU_FEATURE_ALL_BLEND_PRESETS",
           "GPU_FEATURE_ALL_GL_FORMATS", "GPU_FEATURE_BASIC_SHADERS",
           "GPU_FEATURE_ALL_SHADERS", "GPU_WindowFlagEnum",
           "GPU_InitFlagEnum", "GPU_INIT_ENABLE_VSYNC",
           "GPU_INIT_DISABLE_VSYNC", "GPU_INIT_DISABLE_DOUBLE_BUFFER",
           "GPU_INIT_DISABLE_AUTO_VIRTUAL_RESOLUTION",
           "GPU_INIT_REQUEST_COMPATIBILITY_PROFILE",
           "GPU_INIT_USE_ROW_BY_ROW_TEXTURE_UPLOAD_FALLBACK",
           "GPU_INIT_USE_COPY_TEXTURE_UPLOAD_FALLBACK",
           "GPU_DEFAULT_INIT_FLAGS", "GPU_NONE", "GPU_PrimitiveEnum",
           "GPU_POINTS", "GPU_LINES", "GPU_LINE_LOOP", "GPU_LINE_STRIP",
           "GPU_TRIANGLES", "GPU_TRIANGLE_STRIP", "GPU_TRIANGLE_FAN",
           "GPU_BatchFlagEnum", "GPU_BATCH_XY", "GPU_BATCH_XYZ",
           "GPU_BATCH_ST", "GPU_BATCH_RGB", "GPU_BATCH_RGBA",
           "GPU_BATCH_RGB8", "GPU_BATCH_RGBA8", "GPU_BATCH_XY_ST",
           "GPU_BATCH_XYZ_ST", "GPU_BATCH_XY_RGB", "GPU_BATCH_XYZ_RGB",
           "GPU_BATCH_XY_RGBA", "GPU_BATCH_XYZ_RGBA",
           "GPU_BATCH_XY_ST_RGBA", "GPU_BATCH_XYZ_ST_RGBA",
           "GPU_BATCH_XY_RGB8", "GPU_BATCH_XYZ_RGB8",
           "GPU_BATCH_XY_RGBA8", "GPU_BATCH_XYZ_RGBA8",
           "GPU_BATCH_XY_ST_RGBA8", "GPU_BATCH_XYZ_ST_RGBA8",
           "GPU_FlipEnum", "GPU_FLIP_NONE", "GPU_FLIP_HORIZONTAL",
           "GPU_FLIP_VERTICAL", "GPU_TypeEnum", "GPU_TYPE_BYTE",
           "GPU_TYPE_UNSIGNED_BYTE", "GPU_TYPE_SHORT",
           "GPU_TYPE_UNSIGNED_SHORT", "GPU_TYPE_INT",
           "GPU_TYPE_UNSIGNED_INT", "GPU_TYPE_FLOAT", "GPU_TYPE_DOUBLE",
           "GPU_ShaderEnum", "GPU_VERTEX_SHADER", "GPU_FRAGMENT_SHADER",
           "GPU_PIXEL_SHADER", "GPU_GEOMETRY_SHADER",
           "GPU_ShaderLanguageEnum", "GPU_LANGUAGE_NONE",
           "GPU_LANGUAGE_ARB_ASSEMBLY", "GPU_LANGUAGE_GLSL",
           "GPU_LANGUAGE_GLSLES", "GPU_LANGUAGE_HLSL", "GPU_LANGUAGE_CG",
           "GPU_AttributeFormat", "GPU_Attribute", "GPU_AttributeSource",
           "GPU_ErrorEnum", "GPU_ERROR_NONE", "GPU_ERROR_BACKEND_ERROR",
           "GPU_ERROR_DATA_ERROR", "GPU_ERROR_USER_ERROR",
           "GPU_ERROR_UNSUPPORTED_FUNCTION", "GPU_ERROR_NULL_ARGUMENT",
           "GPU_ERROR_FILE_NOT_FOUND", "GPU_ErrorObject",
           "GPU_DebugLevelEnum", "GPU_DEBUG_LEVEL_0", "GPU_DEBUG_LEVEL_1",
           "GPU_DEBUG_LEVEL_2", "GPU_DEBUG_LEVEL_3", "GPU_DEBUG_LEVEL_MAX",
           "GPU_LogLevelEnum", "GPU_LOG_INFO", "GPU_LOG_WARNING",
           "GPU_LOG_ERROR", "GPU_RendererImpl", "GPU_Renderer",
           "GPU_GetCompiledVersion", "GPU_GetLinkedVersion",
           "GPU_SetInitWindow", "GPU_GetInitWindow", "GPU_SetPreInitFlags",
           "GPU_GetPreInitFlags", "GPU_SetRequiredFeatures",
           "GPU_GetRequiredFeatures", "GPU_GetDefaultRendererOrder",
           "GPU_GetRendererOrder", "GPU_SetRendererOrder", "GPU_Init",
           "GPU_InitRenderer", "GPU_InitRendererByID", "GPU_IsFeatureEnabled",
           "GPU_CloseCurrentRenderer", "GPU_Quit", "GPU_SetDebugLevel",
           "GPU_GetDebugLevel", "GPU_LogInfo", "GPU_LogWarning",
           "GPU_LogError", "GPU_SetLogCallback", "GPU_PushErrorCode",
           "GPU_PopErrorCode", "GPU_GetErrorString", "GPU_SetErrorQueueMax",
           "GPU_MakeRendererID", "GPU_GetRendererID",
           "GPU_GetNumRegisteredRenderers", "GPU_GetRegisteredRendererList",
           "GPU_RegisterRenderer", "GPU_ReserveNextRendererEnum",
           "GPU_GetNumActiveRenderers", "GPU_GetActiveRendererList",
           "GPU_GetCurrentRenderer", "GPU_SetCurrentRenderer",
           "GPU_GetRenderer", "GPU_FreeRenderer",
           "GPU_ResetRendererState", "GPU_SetCoordinateMode",
           "GPU_GetCoordinateMode", "GPU_SetDefaultAnchor",
           "GPU_GetDefaultAnchor", "GPU_GetContextTarget",
           "GPU_GetWindowTarget", "GPU_CreateTargetFromWindow",
           "GPU_MakeCurrent", "GPU_SetWindowResolution", "GPU_SetFullscreen",
           "GPU_GetFullscreen", "GPU_SetShapeBlending",
           "GPU_GetBlendModeFromPreset", "GPU_SetShapeBlendFunction",
           "GPU_SetShapeBlendEquation", "GPU_SetShapeBlendMode",
           "GPU_SetLineThickness", "GPU_GetLineThickness",
           "GPU_CreateAliasTarget", "GPU_LoadTarget", "GPU_GetTarget",
           "GPU_FreeTarget", "GPU_SetVirtualResolution",
           "GPU_GetVirtualResolution", "GPU_GetVirtualCoords",
           "GPU_UnsetVirtualResolution", "GPU_MakeRect", "GPU_MakeColor",
           "GPU_SetViewport", "GPU_UnsetViewport", "GPU_GetDefaultCamera",
           "GPU_GetCamera", "GPU_SetCamera", "GPU_EnableCamera",
           "GPU_IsCameraEnabled", "GPU_AddDepthBuffer", "GPU_SetDepthTest",
           "GPU_SetDepthWrite", "GPU_GetPixel", "GPU_SetClipRect",
           "GPU_SetClip", "GPU_UnsetClip", "GPU_IntersectRect",
           "GPU_IntersectClipRect", "GPU_SetTargetColor", "GPU_SetTargetRGB",
           "GPU_SetTargetRGBA", "GPU_UnsetTargetColor", "GPU_LoadSurface",
           "GPU_LoadSurface_RW", "GPU_SaveSurface", "GPU_SaveSurface_RW",
           "GPU_CreateImage", "GPU_CreateImageUsingTexture",
           "GPU_LoadImage", "GPU_LoadImage_RW", "GPU_CreateAliasImage",
           "GPU_CopyImage", "GPU_FreeImage", "GPU_SetImageVirtualResolution",
           "GPU_UnsetImageVirtualResolution", "GPU_UpdateImage",
           "GPU_UpdateImageBytes", "GPU_ReplaceImage", "GPU_SaveImage",
           "GPU_SaveImage_RW", "GPU_GenerateMipmaps", "GPU_SetColor",
           "GPU_SetRGB", "GPU_SetRGBA", "GPU_UnsetColor", "GPU_GetBlending",
           "GPU_SetBlending", "GPU_SetBlendFunction", "GPU_SetBlendEquation",
           "GPU_SetBlendMode", "GPU_SetImageFilter", "GPU_SetAnchor",
           "GPU_GetAnchor", "GPU_GetSnapMode", "GPU_SetSnapMode",
           "GPU_SetWrapMode", "GPU_CopyImageFromSurface",
           "GPU_CopyImageFromTarget", "GPU_CopySurfaceFromTarget",
           "GPU_CopySurfaceFromImage", "GPU_VectorLength",
           "GPU_VectorNormalize", "GPU_VectorDot", "GPU_VectorCross",
           "GPU_VectorCopy", "GPU_VectorApplyMatrix", "GPU_Vector4ApplyMatrix",
           "GPU_MatrixCopy", "GPU_MatrixIdentity", "GPU_MatrixOrtho",
           "GPU_MatrixFrustum", "GPU_MatrixPerspective", "GPU_MatrixLookAt",
           "GPU_MatrixTranslate", "GPU_MatrixScale", "GPU_MatrixRotate",
           "GPU_MatrixMultiply", "GPU_MultiplyAndAssign",
           "GPU_GetMatrixString", "GPU_GetCurrentMatrix", "GPU_GetModelView",
           "GPU_GetProjection", "GPU_GetModelViewProjection",
           "GPU_InitMatrixStack", "GPU_MatrixMode", "GPU_PushMatrix",
           "GPU_PopMatrix", "GPU_LoadIdentity", "GPU_LoadMatrix",
           "GPU_Ortho", "GPU_Frustum", "GPU_Translate", "GPU_Scale",
           "GPU_Rotate", "GPU_MultMatrix", "GPU_Clear", "GPU_ClearColor",
           "GPU_ClearRGB", "GPU_ClearRGBA", "GPU_Blit", "GPU_BlitRotate",
           "GPU_BlitScale", "GPU_BlitTransform", "GPU_BlitTransformX",
           "GPU_BlitRect", "GPU_BlitRectX", "GPU_TriangleBatch",
           "GPU_TriangleBatchX", "GPU_PrimitiveBatch", "GPU_PrimitiveBatchV",
           "GPU_FlushBlitBuffer", "GPU_Flip", "GPU_Pixel", "GPU_Line",
           "GPU_Arc", "GPU_ArcFilled", "GPU_Circle", "GPU_CircleFilled",
           "GPU_Ellipse", "GPU_EllipseFilled", "GPU_Sector",
           "GPU_SectorFilled", "GPU_Tri", "GPU_TriFilled", "GPU_Rectangle",
           "GPU_Rectangle2", "GPU_RectangleFilled", "GPU_RectangleFilled2",
           "GPU_RectangleRound", "GPU_RectangleRound2",
           "GPU_RectangleRoundFilled", "GPU_RectangleRoundFilled2",
           "GPU_Polygon", "GPU_PolygonFilled", "GPU_CreateShaderProgram",
           "GPU_FreeShaderProgram", "GPU_CompileShader_RW",
           "GPU_CompileShader", "GPU_LoadShader", "GPU_LinkShaders",
           "GPU_LinkManyShaders", "GPU_FreeShader", "GPU_AttachShader",
           "GPU_DetachShader", "GPU_LinkShaderProgram",
           "GPU_GetCurrentShaderProgram", "GPU_IsDefaultShaderProgram",
           "GPU_ActivateShaderProgram", "GPU_DeactivateShaderProgram",
           "GPU_GetShaderMessage", "GPU_GetAttributeLocation",
           "GPU_MakeAttributeFormat", "GPU_MakeAttribute",
           "GPU_GetUniformLocation", "GPU_LoadShaderBlock",
           "GPU_SetShaderBlock", "GPU_GetShaderBlock", "GPU_SetShaderImage",
           "GPU_GetUniformiv", "GPU_SetUniformi", "GPU_SetUniformiv",
           "GPU_GetUniformuiv", "GPU_SetUniformui", "GPU_SetUniformuiv",
           "GPU_GetUniformfv", "GPU_SetUniformf", "GPU_SetUniformfv",
           "GPU_GetUniformMatrixfv", "GPU_SetUniformMatrixfv",
           "GPU_SetAttributef", "GPU_SetAttributei", "GPU_SetAttributeui",
           "GPU_SetAttributefv", "GPU_SetAttributeiv", "GPU_SetAttributeuiv",
           "GPU_SetAttributeSource"
           ]

try:
    dll = DLL("SDL2_gpu", ["SDL2_gpu"], os.getenv("PYSDL2_DLL_PATH"))
except RuntimeError as exc:
    raise ImportError(exc)

def get_dll_file():
    """Gets the file name of the loaded SDL_gpu library."""
    return dll.libfile

_bind = dll.bind_function

SDL_GPU_VERSION_MAJOR = 0
SDL_GPU_VERSION_MINOR = 11
SDL_GPU_VERSION_PATCH = 0

# Since GPU_bool is based on a conditional #define, we don't know if it is
# actually a bool or an int, so just assume it's an int because there's no
# way to know what was defined at compile-time
GPU_bool = c_int

GPU_FALSE = 0
GPU_TRUE = 1

# Forward declaration for GPU_Target
class GPU_Target(Structure):
    pass


# Forward declaration for GPU_Renderer
class GPU_Renderer(Structure):
    pass


# GPU_Rect structure - mostly taken from PySDL2's rect.py
# Didn't include __eq__ and __ne__ because of floating point equality issues
class GPU_Rect(Structure):
    _fields_ = [("x", c_float), ("y", c_float),
                ("w", c_float), ("h", c_float)]

    def __init__(self, x=0, y=0, w=0, h=0):
        super(GPU_Rect, self).__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return "GPU_Rect(x=%d, y=%d, w=%d, h=%d)" % (self.x, self.y, self.w,
                                                     self.h)

    def __copy__(self):
        return GPU_Rect(self.x, self.y, self.w, self.h)

    def __deepcopy__(self, memo):
        return GPU_Rect(self.x, self.y, self.w, self.h)


# Used for GPU_GetDefaultRendererOrder()
GPU_RENDERER_ORDER_MAX = 10

GPU_RendererEnum = Uint32
GPU_RENDERER_UNKNOWN = 0  # invalid value
GPU_RENDERER_OPENGL_1_BASE = 1
GPU_RENDERER_OPENGL_1 = 2
GPU_RENDERER_OPENGL_2 = 3
GPU_RENDERER_OPENGL_3 = 4
GPU_RENDERER_OPENGL_4 = 5
GPU_RENDERER_GLES_1 = 11
GPU_RENDERER_GLES_2 = 12
GPU_RENDERER_GLES_3 = 13
GPU_RENDERER_D3D9 = 21
GPU_RENDERER_D3D10 = 22
GPU_RENDERER_D3D11 = 23

class GPU_RendererID(Structure):
    _fields_ = [("name", c_char_p),
                ("renderer", GPU_RendererEnum),
                ("major_version", c_int),
                ("minor_version", c_int)]


GPU_BlendFuncEnum = c_int
GPU_FUNC_ZERO = 0
GPU_FUNC_ONE = 1
GPU_FUNC_SRC_COLOR = 0x0300
GPU_FUNC_DST_COLOR = 0x0306
GPU_FUNC_ONE_MINUS_SRC = 0x0301
GPU_FUNC_ONE_MINUS_DST = 0x0307
GPU_FUNC_SRC_ALPHA = 0x0302
GPU_FUNC_DST_ALPHA = 0x0304
GPU_FUNC_ONE_MINUS_SRC_ALPHA = 0x0303
GPU_FUNC_ONE_MINUS_DST_ALPHA = 0x0305

GPU_BlendEqEnum = c_int
GPU_EQ_ADD = 0x8006
GPU_EQ_SUBTRACT = 0x800A
GPU_EQ_REVERSE_SUBTRACT = 0x800B

class GPU_BlendMode(Structure):
    _fields_ = [("source_color", GPU_BlendFuncEnum),
                ("dest_color", GPU_BlendFuncEnum),
                ("source_alpha", GPU_BlendFuncEnum),
                ("dest_alpha", GPU_BlendFuncEnum),
                ("color_equation", GPU_BlendEqEnum),
                ("alpha_equation", GPU_BlendEqEnum)]


GPU_BlendPresetEnum = c_int
GPU_BLEND_NORMAL = 0
GPU_BLEND_PREMULTIPLIED_ALPHA = 1
GPU_BLEND_MULTIPLY = 2
GPU_BLEND_ADD = 3
GPU_BLEND_SUBTRACT = 4
GPU_BLEND_MOD_ALPHA = 5
GPU_BLEND_SET_ALPHA = 6
GPU_BLEND_SET = 7
GPU_BLEND_NORMAL_KEEP_ALPHA = 8
GPU_BLEND_NORMAL_ADD_ALPHA = 9
GPU_BLEND_NORMAL_FACTOR_ALPHA = 10

GPU_FilterEnum = c_int
GPU_FILTER_NEAREST = 0
GPU_FILTER_LINEAR = 1
GPU_FILTER_LINEAR_MIPMAP = 2

GPU_SnapEnum = c_int
GPU_SNAP_NONE = 0
GPU_SNAP_POSITION = 1
GPU_SNAP_DIMENSIONS = 2
GPU_SNAP_POSITION_AND_DIMENSIONS = 3

GPU_WrapEnum = c_int
GPU_WRAP_NONE = 0
GPU_WRAP_REPEAT = 1
GPU_WRAP_MIRRORED = 2

GPU_FormatEnum = c_int
GPU_FORMAT_LUMINANCE = 1
GPU_FORMAT_LUMINANCE_ALPHA = 2
GPU_FORMAT_RGB = 3
GPU_FORMAT_RGBA = 4
GPU_FORMAT_ALPHA = 5
GPU_FORMAT_RG = 6
GPU_FORMAT_YCbCr422 = 7
GPU_FORMAT_YCbCr420P = 8
GPU_FORMAT_BGR = 9
GPU_FORMAT_BGRA = 10
GPU_FORMAT_ABGR = 11

GPU_FileFormatEnum = c_int
GPU_FILE_AUTO = 0
GPU_FILE_PNG = 1
GPU_FILE_BMP = 2
GPU_FILE_TGA = 3

class GPU_Image(Structure):
    _fields_ = [("renderer", POINTER(GPU_Renderer)),
                ("context_target", POINTER(GPU_Target)),
                ("target", POINTER(GPU_Target)),
                ("w", Uint16),
                ("h", Uint16),
                ("using_virtual_resolution", GPU_bool),
                ("format", GPU_FormatEnum),
                ("num_layers", c_int),
                ("bytes_per_pixel", c_int),
                ("base_w", Uint16),
                ("base_h", Uint16),
                ("texture_w", Uint16),
                ("texture_h", Uint16),
                ("has_mipmaps", GPU_bool),
                ("anchor_x", c_float),
                ("anchor_y", c_float),
                ("color", SDL_Color),
                ("use_blending", GPU_bool),
                ("blend_mode", GPU_BlendMode),
                ("filter_mode", GPU_FilterEnum),
                ("snap_mode", GPU_SnapEnum),
                ("wrap_mode_x", GPU_WrapEnum),
                ("wrap_mode_y", GPU_WrapEnum),
                ("data", c_void_p),
                ("refcount", c_int),
                ("is_alias", GPU_bool)]


class GPU_Camera(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float),
                ("angle", c_float),
                ("zoom", c_float),
                ("z_near", c_float),
                ("z_far", c_float)]


class GPU_ShaderBlock(Structure):
    _fields_ = [("position_loc", c_int),
                ("texcoord_loc", c_int),
                ("color_loc", c_int),
                ("modelViewProjection_loc", c_int)]


# Used for GPU_MatrixMode()
GPU_MODELVIEW = 0
GPU_PROJECTION = 1

class GPU_MatrixStack(Structure):
    _fields_ = [("storage_size", c_uint),
                ("size", c_uint),
                ("matrix", POINTER(POINTER(c_float)))]


class GPU_Context(Structure):
    _fields_ = [("context", c_void_p),
                ("failed", GPU_bool),
                ("windowID", Uint32),
                ("window_w", c_int),
                ("window_h", c_int),
                ("drawable_w", c_int),
                ("drawable_h", c_int),
                ("stored_window_w", c_int),
                ("stored_window_h", c_int),
                ("current_shader_program", Uint32),
                ("default_textured_shader_program", Uint32),
                ("default_untextured_shader_program", Uint32),
                ("current_shader_block", GPU_ShaderBlock),
                ("default_textured_shader_block", GPU_ShaderBlock),
                ("default_untextured_shader_block", GPU_ShaderBlock),
                ("shapes_use_blending", GPU_bool),
                ("shapes_blend_mode", GPU_BlendMode),
                ("line_thickness", c_float),
                ("use_texturing", GPU_bool),
                ("matrix_mode", c_int),
                ("projection_matrix", GPU_MatrixStack),
                ("modelview_matrix", GPU_MatrixStack),
                ("refcount", c_int),
                ("data", c_void_p)]


# Actual definition of GPU_Target
GPU_Target._fields_ = [("renderer", POINTER(GPU_Renderer)),
                       ("context_target", POINTER(GPU_Target)),
                       ("image", POINTER(GPU_Image)),
                       ("data", c_void_p),
                       ("w", Uint16),
                       ("h", Uint16),
                       ("using_virtual_resolution", GPU_bool),
                       ("base_w", Uint16),
                       ("base_h", Uint16),
                       ("use_clip_rect", GPU_bool),
                       ("clip_rect", GPU_Rect),
                       ("use_color", GPU_bool),
                       ("color", SDL_Color),
                       ("viewport", GPU_Rect),
                       ("camera", GPU_Camera),
                       ("use_camera", GPU_bool),
                       ("use_depth_test", GPU_bool),
                       ("use_depth_write", GPU_bool),
                       ("context", POINTER(GPU_Context)),
                       ("refcount", c_int),
                       ("is_alias", GPU_bool)]


GPU_FeatureEnum = Uint32
GPU_FEATURE_NON_POWER_OF_TWO = 0x1
GPU_FEATURE_RENDER_TARGETS = 0x2
GPU_FEATURE_BLEND_EQUATIONS = 0x4
GPU_FEATURE_BLEND_FUNC_SEPARATE = 0x8
GPU_FEATURE_BLEND_EQUATIONS_SEPARATE = 0x10
GPU_FEATURE_GL_BGR = 0x20
GPU_FEATURE_GL_BGRA = 0x40
GPU_FEATURE_GL_ABGR = 0x80
GPU_FEATURE_VERTEX_SHADER = 0x100
GPU_FEATURE_FRAGMENT_SHADER = 0x200
GPU_FEATURE_PIXEL_SHADER = 0x200
GPU_FEATURE_GEOMETRY_SHADER = 0x400
GPU_FEATURE_WRAP_REPEAT_MIRRORED = 0x800
GPU_FEATURE_CORE_FRAMEBUFFER_OBJECTS = 0x1000

GPU_FEATURE_ALL_BASE = GPU_FEATURE_RENDER_TARGETS
GPU_FEATURE_ALL_BLEND_PRESETS = (GPU_FEATURE_BLEND_EQUATIONS |
                                 GPU_FEATURE_BLEND_FUNC_SEPARATE)
GPU_FEATURE_ALL_GL_FORMATS = (GPU_FEATURE_GL_BGR |
                              GPU_FEATURE_GL_BGRA |
                              GPU_FEATURE_GL_ABGR)
GPU_FEATURE_BASIC_SHADERS = (GPU_FEATURE_FRAGMENT_SHADER |
                             GPU_FEATURE_VERTEX_SHADER)
GPU_FEATURE_ALL_SHADERS = (GPU_FEATURE_FRAGMENT_SHADER |
                           GPU_FEATURE_VERTEX_SHADER |
                           GPU_FEATURE_GEOMETRY_SHADER)

GPU_WindowFlagEnum = Uint32

GPU_InitFlagEnum = Uint32
GPU_INIT_ENABLE_VSYNC = 0x1
GPU_INIT_DISABLE_VSYNC = 0x2
GPU_INIT_DISABLE_DOUBLE_BUFFER = 0x4
GPU_INIT_DISABLE_AUTO_VIRTUAL_RESOLUTION = 0x8
GPU_INIT_REQUEST_COMPATIBILITY_PROFILE = 0x10
GPU_INIT_USE_ROW_BY_ROW_TEXTURE_UPLOAD_FALLBACK = 0x20
GPU_INIT_USE_COPY_TEXTURE_UPLOAD_FALLBACK = 0x40

GPU_DEFAULT_INIT_FLAGS = 0

GPU_NONE = 0x0

GPU_PrimitiveEnum = Uint32
GPU_POINTS = 0x0
GPU_LINES = 0x1
GPU_LINE_LOOP = 0x2
GPU_LINE_STRIP = 0x3
GPU_TRIANGLES = 0x4
GPU_TRIANGLE_STRIP = 0x5
GPU_TRIANGLE_FAN = 0x6

GPU_BatchFlagEnum = Uint32
GPU_BATCH_XY = 0x1
GPU_BATCH_XYZ = 0x2
GPU_BATCH_ST = 0x4
GPU_BATCH_RGB = 0x8
GPU_BATCH_RGBA = 0x10
GPU_BATCH_RGB8 = 0x20
GPU_BATCH_RGBA8 = 0x40

GPU_BATCH_XY_ST = (GPU_BATCH_XY | GPU_BATCH_ST)
GPU_BATCH_XYZ_ST = (GPU_BATCH_XYZ | GPU_BATCH_ST)
GPU_BATCH_XY_RGB = (GPU_BATCH_XY | GPU_BATCH_RGB)
GPU_BATCH_XYZ_RGB = (GPU_BATCH_XYZ | GPU_BATCH_RGB)
GPU_BATCH_XY_RGBA = (GPU_BATCH_XY | GPU_BATCH_RGBA)
GPU_BATCH_XYZ_RGBA = (GPU_BATCH_XYZ | GPU_BATCH_RGBA)
GPU_BATCH_XY_ST_RGBA = (GPU_BATCH_XY | GPU_BATCH_ST | GPU_BATCH_RGBA)
GPU_BATCH_XYZ_ST_RGBA = (GPU_BATCH_XYZ | GPU_BATCH_ST | GPU_BATCH_RGBA)
GPU_BATCH_XY_RGB8 = (GPU_BATCH_XY | GPU_BATCH_RGB8)
GPU_BATCH_XYZ_RGB8 = (GPU_BATCH_XYZ | GPU_BATCH_RGB8)
GPU_BATCH_XY_RGBA8 = (GPU_BATCH_XY | GPU_BATCH_RGBA8)
GPU_BATCH_XYZ_RGBA8 = (GPU_BATCH_XYZ | GPU_BATCH_RGBA8)
GPU_BATCH_XY_ST_RGBA8 = (GPU_BATCH_XY | GPU_BATCH_ST | GPU_BATCH_RGBA8)
GPU_BATCH_XYZ_ST_RGBA8 = (GPU_BATCH_XYZ | GPU_BATCH_ST | GPU_BATCH_RGBA8)

GPU_FlipEnum = Uint32
GPU_FLIP_NONE = 0x0
GPU_FLIP_HORIZONTAL = 0x1
GPU_FLIP_VERTICAL = 0x2

GPU_TypeEnum = Uint32
GPU_TYPE_BYTE = 0x1400
GPU_TYPE_UNSIGNED_BYTE = 0x1401
GPU_TYPE_SHORT = 0x1402
GPU_TYPE_UNSIGNED_SHORT = 0x1403
GPU_TYPE_INT = 0x1404
GPU_TYPE_UNSIGNED_INT = 0x1405
GPU_TYPE_FLOAT = 0x1406
GPU_TYPE_DOUBLE = 0x140A

GPU_ShaderEnum = c_int
GPU_VERTEX_SHADER = 0
GPU_FRAGMENT_SHADER = 1
GPU_PIXEL_SHADER = 1
GPU_GEOMETRY_SHADER = 2

GPU_ShaderLanguageEnum = c_int
GPU_LANGUAGE_NONE = 0
GPU_LANGUAGE_ARB_ASSEMBLY = 1
GPU_LANGUAGE_GLSL = 2
GPU_LANGUAGE_GLSLES = 3
GPU_LANGUAGE_HLSL = 4
GPU_LANGUAGE_CG = 5

class GPU_AttributeFormat(Structure):
    _fields_ = [("is_per_sprite", GPU_bool),
                ("num_elems_per_value", c_int),
                ("type", GPU_TypeEnum),
                ("normalize", GPU_bool),
                ("stride_bytes", c_int),
                ("offset_bytes", c_int)]


class GPU_Attribute(Structure):
    _fields_ = [("location", c_int),
                ("values", c_void_p),
                ("format", GPU_AttributeFormat)]


class GPU_AttributeSource(Structure):
    _fields_ = [("enabled", GPU_bool),
                ("num_values", c_int),
                ("next_value", c_void_p),
                ("per_vertex_storage_stride_bytes", c_int),
                ("per_vertex_storage_offset_bytes", c_int),
                ("per_vertex_storage_size", c_int),
                ("per_vertex_storage", c_void_p),
                ("attribute", GPU_Attribute)]


GPU_ErrorEnum = c_int
GPU_ERROR_NONE = 0
GPU_ERROR_BACKEND_ERROR = 1
GPU_ERROR_DATA_ERROR = 2
GPU_ERROR_USER_ERROR = 3
GPU_ERROR_UNSUPPORTED_FUNCTION = 4
GPU_ERROR_NULL_ARGUMENT = 5
GPU_ERROR_FILE_NOT_FOUND = 6

class GPU_ErrorObject(Structure):
    _fields_ = [("function", c_char_p),
                ("error", GPU_ErrorEnum),
                ("details", c_char_p)]


GPU_DebugLevelEnum = c_int
GPU_DEBUG_LEVEL_0 = 0
GPU_DEBUG_LEVEL_1 = 1
GPU_DEBUG_LEVEL_2 = 2
GPU_DEBUG_LEVEL_3 = 3
GPU_DEBUG_LEVEL_MAX = 3

GPU_LogLevelEnum = c_int
GPU_LOG_INFO = 0
GPU_LOG_WARNING = 1
GPU_LOG_ERROR = 2

class GPU_RendererImpl(Structure):
    pass


# Actual definition of GPU_Renderer
GPU_Renderer._fields_ = [("id", GPU_RendererID),
                         ("requested_id", GPU_RendererID),
                         ("SDL_init_flags", GPU_WindowFlagEnum),
                         ("GPU_init_flags", GPU_InitFlagEnum),
                         ("shader_language", GPU_ShaderLanguageEnum),
                         ("min_shader_version", c_int),
                         ("max_shader_version", c_int),
                         ("enabled_features", GPU_FeatureEnum),
                         ("current_context_target", POINTER(GPU_Target)),
                         ("coordinate_mode", GPU_bool),
                         ("default_image_anchor_x", c_float),
                         ("default_image_anchor_y", c_float),
                         ("impl", POINTER(GPU_RendererImpl))]


# This function may be inline in the header, so it may not be exported
# by SDL_gpu, and so let's just reimplement it here
def GPU_GetCompiledVersion():
    v = SDL_version()
    v.major = SDL_GPU_VERSION_MAJOR
    v.minor = SDL_GPU_VERSION_MINOR
    v.patch = SDL_GPU_VERSION_PATCH
    return v

GPU_GetLinkedVersion = _bind("GPU_GetLinkedVersion", None, SDL_version)
GPU_SetInitWindow = _bind("GPU_SetInitWindow", [Uint32], None)
GPU_GetInitWindow = _bind("GPU_GetInitWindow", None, Uint32)
GPU_SetPreInitFlags = _bind("GPU_SetPreInitFlags", [GPU_InitFlagEnum], None)
GPU_GetPreInitFlags = _bind("GPU_GetPreInitFlags", None, GPU_InitFlagEnum)
GPU_SetRequiredFeatures = _bind("GPU_SetRequiredFeatures", [GPU_FeatureEnum], None)
GPU_GetRequiredFeatures = _bind("GPU_GetRequiredFeatures", None, GPU_FeatureEnum)
GPU_GetDefaultRendererOrder = _bind("GPU_GetDefaultRendererOrder", [POINTER(c_int), POINTER(GPU_RendererID)], None)
GPU_GetRendererOrder = _bind("GPU_GetRendererOrder", [POINTER(c_int), POINTER(GPU_RendererID)], None)
GPU_SetRendererOrder = _bind("GPU_SetRendererOrder", [c_int, POINTER(GPU_RendererID)], None)
GPU_Init = _bind("GPU_Init", [Uint16, Uint16, GPU_WindowFlagEnum], POINTER(GPU_Target))
GPU_InitRenderer = _bind("GPU_InitRenderer", [GPU_RendererEnum, Uint16, Uint16, GPU_WindowFlagEnum], POINTER(GPU_Target))
GPU_InitRendererByID = _bind("GPU_InitRendererByID", [GPU_RendererID, Uint16, Uint16, GPU_WindowFlagEnum], POINTER(GPU_Target))
GPU_IsFeatureEnabled = _bind("GPU_IsFeatureEnabled", [GPU_FeatureEnum], GPU_bool)
GPU_CloseCurrentRenderer = _bind("GPU_CloseCurrentRenderer", None, None)
GPU_Quit = _bind("GPU_Quit", None, None)

GPU_SetDebugLevel = _bind("GPU_SetDebugLevel", [GPU_DebugLevelEnum], None)
GPU_GetDebugLevel = _bind("GPU_GetDebugLevel", None, GPU_DebugLevelEnum)
# The next three functions are actually variadic, but let's just handle them
# the way PySDL2 did for now
GPU_LogInfo = _bind("GPU_LogInfo", [c_char_p], None)
GPU_LogWarning = _bind("GPU_LogWarning", [c_char_p], None)
GPU_LogError = _bind("GPU_LogError", [c_char_p], None)
# I don't know if there's a way to 'translate' GPU_SetLogCallback into ctypes,
# so just expose the function as-is
GPU_SetLogCallback = dll._dll.GPU_SetLogCallback
# GPU_PushErrorCode is actually variadic
GPU_PushErrorCode = _bind("GPU_PushErrorCode", [c_char_p, GPU_ErrorEnum, c_char_p], None)
GPU_PopErrorCode = _bind("GPU_PopErrorCode", None, GPU_ErrorObject)
GPU_GetErrorString = _bind("GPU_GetErrorString", [GPU_ErrorEnum], c_char_p)
GPU_SetErrorQueueMax = _bind("GPU_SetErrorQueueMax", [c_uint], None)

GPU_MakeRendererID = _bind("GPU_MakeRendererID", [c_char_p, GPU_RendererEnum, c_int, c_int], GPU_RendererID)
GPU_GetRendererID = _bind("GPU_GetRendererID", [GPU_RendererEnum], GPU_RendererID)
GPU_GetNumRegisteredRenderers = _bind("GPU_GetNumRegisteredRenderers", None, c_int)
GPU_GetRegisteredRendererList = _bind("GPU_GetRegisteredRendererList", [POINTER(GPU_RendererID)], None)
# TODO: should the programmer be able to access these easily?
create_renderer = CFUNCTYPE(POINTER(GPU_Renderer), GPU_RendererID)
free_renderer = CFUNCTYPE(None, POINTER(GPU_Renderer))
GPU_RegisterRenderer = _bind("GPU_RegisterRenderer", [GPU_RendererID, create_renderer, free_renderer], None)

GPU_ReserveNextRendererEnum = _bind("GPU_ReserveNextRendererEnum", None, GPU_RendererEnum)
GPU_GetNumActiveRenderers = _bind("GPU_GetNumActiveRenderers", None, c_int)
GPU_GetActiveRendererList = _bind("GPU_GetActiveRendererList", [POINTER(GPU_RendererID)], None)
GPU_GetCurrentRenderer = _bind("GPU_GetCurrentRenderer", None, POINTER(GPU_Renderer))
GPU_SetCurrentRenderer = _bind("GPU_SetCurrentRenderer", [GPU_RendererID], None)
GPU_GetRenderer = _bind("GPU_GetRenderer", [GPU_RendererID], POINTER(GPU_Renderer))
GPU_FreeRenderer = _bind("GPU_FreeRenderer", [POINTER(GPU_Renderer)], None)
GPU_ResetRendererState = _bind("GPU_ResetRendererState", None, None)
GPU_SetCoordinateMode = _bind("GPU_SetCoordinateMode", [GPU_bool], None)
GPU_GetCoordinateMode = _bind("GPU_GetCoordinateMode", None, GPU_bool)
GPU_SetDefaultAnchor = _bind("GPU_SetDefaultAnchor", [c_float, c_float], None)
GPU_GetDefaultAnchor = _bind("GPU_GetDefaultAnchor", [POINTER(c_float), POINTER(c_float)], None)

GPU_GetContextTarget = _bind("GPU_GetContextTarget", None, POINTER(GPU_Target))
GPU_GetWindowTarget = _bind("GPU_GetWindowTarget", [Uint32], POINTER(GPU_Target))
GPU_CreateTargetFromWindow = _bind("GPU_CreateTargetFromWindow", [Uint32], POINTER(GPU_Target))
GPU_MakeCurrent = _bind("GPU_MakeCurrent", [POINTER(GPU_Target), Uint32], None)
GPU_SetWindowResolution = _bind("GPU_SetWindowResolution", [Uint16, Uint16], GPU_bool)
GPU_SetFullscreen = _bind("GPU_SetFullscreen", [GPU_bool, GPU_bool], GPU_bool)
GPU_GetFullscreen = _bind("GPU_GetFullscreen", None, GPU_bool)
GPU_SetShapeBlending = _bind("GPU_SetShapeBlending", [GPU_bool], None)
GPU_GetBlendModeFromPreset = _bind("GPU_GetBlendModeFromPreset", [GPU_BlendPresetEnum], GPU_BlendMode)
GPU_SetShapeBlendFunction = _bind("GPU_SetShapeBlendFunction", [GPU_BlendFuncEnum, GPU_BlendFuncEnum, GPU_BlendFuncEnum, GPU_BlendFuncEnum], None)
GPU_SetShapeBlendEquation = _bind("GPU_SetShapeBlendEquation", [GPU_BlendEqEnum, GPU_BlendEqEnum], None)
GPU_SetShapeBlendMode = _bind("GPU_SetShapeBlendMode", [GPU_BlendPresetEnum], None)
GPU_SetLineThickness = _bind("GPU_SetLineThickness", [c_float], c_float)
GPU_GetLineThickness = _bind("GPU_GetLineThickness", None, c_float)

GPU_CreateAliasTarget = _bind("GPU_CreateAliasTarget", [POINTER(GPU_Target)], POINTER(GPU_Target))
GPU_LoadTarget = _bind("GPU_LoadTarget", [POINTER(GPU_Image)], POINTER(GPU_Target))
GPU_GetTarget = _bind("GPU_GetTarget", [POINTER(GPU_Image)], POINTER(GPU_Target))
GPU_FreeTarget = _bind("GPU_FreeTarget", [POINTER(GPU_Target)], None)
GPU_SetVirtualResolution = _bind("GPU_SetVirtualResolution", [POINTER(GPU_Target), Uint16, Uint16], None)
GPU_GetVirtualResolution = _bind("GPU_GetVirtualResolution", [POINTER(GPU_Target), POINTER(Uint16), POINTER(Uint16)], None)
GPU_GetVirtualCoords = _bind("GPU_GetVirtualCoords", [POINTER(GPU_Target), POINTER(c_float), POINTER(c_float), c_float, c_float], None)
GPU_UnsetVirtualResolution = _bind("GPU_UnsetVirtualResolution", [POINTER(GPU_Target)], None)
GPU_MakeRect = _bind("GPU_MakeRect", [c_float, c_float, c_float, c_float], GPU_Rect)
GPU_MakeColor = _bind("GPU_MakeColor", [Uint8, Uint8, Uint8, Uint8], SDL_Color)
GPU_SetViewport = _bind("GPU_SetViewport", [POINTER(GPU_Target), GPU_Rect], None)
GPU_UnsetViewport = _bind("GPU_UnsetViewport", [POINTER(GPU_Target)], None)
GPU_GetDefaultCamera = _bind("GPU_GetDefaultCamera", None, GPU_Camera)
GPU_GetCamera = _bind("GPU_GetCamera", [POINTER(GPU_Target)], GPU_Camera)
GPU_SetCamera = _bind("GPU_SetCamera", [POINTER(GPU_Target), POINTER(GPU_Camera)], GPU_Camera)
GPU_EnableCamera = _bind("GPU_EnableCamera", [POINTER(GPU_Target), GPU_bool], None)
GPU_IsCameraEnabled = _bind("GPU_IsCameraEnabled", [POINTER(GPU_Target)], GPU_bool)
GPU_AddDepthBuffer = _bind("GPU_AddDepthBuffer", [POINTER(GPU_Target)], GPU_bool)
GPU_SetDepthTest = _bind("GPU_SetDepthTest", [POINTER(GPU_Target)], GPU_bool)
GPU_SetDepthWrite = _bind("GPU_SetDepthWrite", [POINTER(GPU_Target)], GPU_bool)
GPU_GetPixel = _bind("GPU_GetPixel", [POINTER(GPU_Target), Sint16, Sint16], SDL_Color)
GPU_SetClipRect = _bind("GPU_SetClipRect", [POINTER(GPU_Target), GPU_Rect], GPU_Rect)
GPU_SetClip = _bind("GPU_SetClip", [POINTER(GPU_Target), Sint16, Sint16, Uint16, Uint16], GPU_Rect)
GPU_UnsetClip = _bind("GPU_UnsetClip", [POINTER(GPU_Target)], None)
GPU_IntersectRect = _bind("GPU_IntersectRect", [GPU_Rect, GPU_Rect, POINTER(GPU_Rect)], GPU_bool)
GPU_IntersectClipRect = _bind("GPU_IntersectClipRect", [POINTER(GPU_Target), GPU_Rect, POINTER(GPU_Rect)], GPU_bool)
GPU_SetTargetColor = _bind("GPU_SetTargetColor", [POINTER(GPU_Target), SDL_Color], None)
GPU_SetTargetRGB = _bind("GPU_SetTargetRGB", [POINTER(GPU_Target), Uint8, Uint8, Uint8], None)
GPU_SetTargetRGBA = _bind("GPU_SetTargetRGBA", [POINTER(GPU_Target), Uint8, Uint8, Uint8, Uint8], None)
GPU_UnsetTargetColor = _bind("GPU_UnsetTargetColor", [POINTER(GPU_Target)], None)

GPU_LoadSurface = _bind("GPU_LoadSurface", [c_char_p], POINTER(SDL_Surface))
GPU_LoadSurface_RW = _bind("GPU_LoadSurface_RW", [POINTER(SDL_RWops), GPU_bool], POINTER(SDL_Surface))
GPU_SaveSurface = _bind("GPU_SaveSurface", [POINTER(SDL_Surface), c_char_p, GPU_FileFormatEnum], GPU_bool)
GPU_SaveSurface_RW = _bind("GPU_SaveSurface_RW", [POINTER(SDL_Surface), POINTER(SDL_RWops), GPU_FileFormatEnum], GPU_bool)

GPU_CreateImage = _bind("GPU_CreateImage", [Uint16, Uint16, GPU_FormatEnum], POINTER(GPU_Image))
GPU_CreateImageUsingTexture = _bind("GPU_CreateImageUsingTexture", [Uint32, GPU_bool], POINTER(GPU_Image))
GPU_LoadImage = _bind("GPU_LoadImage", [c_char_p], POINTER(GPU_Image))
GPU_LoadImage_RW = _bind("GPU_LoadImage_RW", [POINTER(SDL_RWops), GPU_bool], POINTER(GPU_Image))
GPU_CreateAliasImage = _bind("GPU_CreateAliasImage", [POINTER(GPU_Image)], POINTER(GPU_Image))
GPU_CopyImage = _bind("GPU_CopyImage", [POINTER(GPU_Image)], POINTER(GPU_Image))
GPU_FreeImage = _bind("GPU_FreeImage", [POINTER(GPU_Image)], None)
GPU_SetImageVirtualResolution = _bind("GPU_SetImageVirtualResolution", [POINTER(GPU_Image), Uint16, Uint16], None)
GPU_UnsetImageVirtualResolution = _bind("GPU_UnsetImageVirtualResolution", [POINTER(GPU_Image)], None)
GPU_UpdateImage = _bind("GPU_UpdateImage", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(SDL_Surface), POINTER(GPU_Rect)], None)
GPU_UpdateImageBytes = _bind("GPU_UpdateImageBytes", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(c_ubyte), c_int], None)
GPU_ReplaceImage = _bind("GPU_ReplaceImage", [POINTER(GPU_Image), POINTER(SDL_Surface), POINTER(GPU_Rect)], GPU_bool)
GPU_SaveImage = _bind("GPU_SaveImage", [POINTER(GPU_Image), c_char_p, GPU_FileFormatEnum], GPU_bool)
GPU_SaveImage_RW = _bind("GPU_SaveImage_RW", [POINTER(GPU_Image), POINTER(SDL_RWops), GPU_FileFormatEnum], GPU_bool)
GPU_GenerateMipmaps = _bind("GPU_GenerateMipmaps", [POINTER(GPU_Image)], None)
GPU_SetColor = _bind("GPU_SetColor", [POINTER(GPU_Image), SDL_Color], None)
GPU_SetRGB = _bind("GPU_SetRGB", [POINTER(GPU_Image), Uint8, Uint8, Uint8], None)
GPU_SetRGBA = _bind("GPU_SetRGBA", [POINTER(GPU_Image), Uint8, Uint8, Uint8, Uint8], None)
GPU_UnsetColor = _bind("GPU_UnsetColor", [POINTER(GPU_Image)], None)
GPU_GetBlending = _bind("GPU_GetBlending", [POINTER(GPU_Image)], GPU_bool)
GPU_SetBlending = _bind("GPU_SetBlending", [POINTER(GPU_Image), GPU_bool], None)
GPU_SetBlendFunction = _bind("GPU_SetBlendFunction", [POINTER(GPU_Image), GPU_BlendFuncEnum, GPU_BlendFuncEnum, GPU_BlendFuncEnum, GPU_BlendFuncEnum], None)
GPU_SetBlendEquation = _bind("GPU_SetBlendEquation", [POINTER(GPU_Image), GPU_BlendEqEnum, GPU_BlendEqEnum], None)
GPU_SetBlendMode = _bind("GPU_SetBlendMode", [POINTER(GPU_Image), GPU_BlendPresetEnum], None)
GPU_SetImageFilter = _bind("GPU_SetImageFilter", [POINTER(GPU_Image), GPU_FilterEnum], None)
GPU_SetAnchor = _bind("GPU_SetAnchor", [POINTER(GPU_Image), c_float, c_float], None)
GPU_GetAnchor = _bind("GPU_GetAnchor", [POINTER(GPU_Image), POINTER(c_float), POINTER(c_float)], None)
GPU_GetSnapMode = _bind("GPU_GetSnapMode", [POINTER(GPU_Image)], GPU_SnapEnum)
GPU_SetSnapMode = _bind("GPU_SetSnapMode", [POINTER(GPU_Image), GPU_SnapEnum], None)
GPU_SetWrapMode = _bind("GPU_SetWrapMode", [POINTER(GPU_Image), GPU_WrapEnum, GPU_WrapEnum], None)

GPU_CopyImageFromSurface = _bind("GPU_CopyImageFromSurface", [POINTER(SDL_Surface)], POINTER(GPU_Image))
GPU_CopyImageFromTarget = _bind("GPU_CopyImageFromTarget", [POINTER(GPU_Target)], POINTER(GPU_Image))
GPU_CopySurfaceFromTarget = _bind("GPU_CopySurfaceFromTarget", [POINTER(GPU_Target)], POINTER(SDL_Surface))
GPU_CopySurfaceFromImage = _bind("GPU_CopySurfaceFromImage", [POINTER(GPU_Image)], POINTER(SDL_Surface))

GPU_VectorLength = _bind("GPU_VectorLength", [POINTER(c_float)], c_float)
GPU_VectorNormalize = _bind("GPU_VectorNormalize", [POINTER(c_float)], None)
GPU_VectorDot = _bind("GPU_VectorDot", [POINTER(c_float), POINTER(c_float)], c_float)
GPU_VectorCross = _bind("GPU_VectorCross", [POINTER(c_float), POINTER(c_float), POINTER(c_float)], None)
GPU_VectorCopy = _bind("GPU_VectorCopy", [POINTER(c_float), POINTER(c_float)], None)
GPU_VectorApplyMatrix = _bind("GPU_VectorApplyMatrix", [POINTER(c_float), POINTER(c_float)], None)
GPU_Vector4ApplyMatrix = _bind("GPU_Vector4ApplyMatrix", [POINTER(c_float), POINTER(c_float)], None)

GPU_MatrixCopy = _bind("GPU_MatrixCopy", [POINTER(c_float), POINTER(c_float)], None)
GPU_MatrixIdentity = _bind("GPU_MatrixIdentity", [POINTER(c_float)], None)
GPU_MatrixOrtho = _bind("GPU_MatrixOrtho", [POINTER(c_float), c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_MatrixFrustum = _bind("GPU_MatrixFrustum", [POINTER(c_float), c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_MatrixPerspective = _bind("GPU_MatrixPerspective", [POINTER(c_float), c_float, c_float, c_float, c_float], None)
GPU_MatrixLookAt = _bind("GPU_MatrixLookAt", [POINTER(c_float), c_float, c_float, c_float, c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_MatrixTranslate = _bind("GPU_MatrixTranslate", [POINTER(c_float), c_float, c_float, c_float], None)
GPU_MatrixScale = _bind("GPU_MatrixScale", [POINTER(c_float), c_float, c_float, c_float], None)
GPU_MatrixRotate = _bind("GPU_MatrixRotate", [POINTER(c_float), c_float, c_float, c_float, c_float], None)
GPU_MatrixMultiply = _bind("GPU_MatrixMultiply", [POINTER(c_float), POINTER(c_float), POINTER(c_float)], None)
GPU_MultiplyAndAssign = _bind("GPU_MultiplyAndAssign", [POINTER(c_float), POINTER(c_float)], None)

GPU_GetMatrixString = _bind("GPU_GetMatrixString", [POINTER(c_float)], c_char_p)
GPU_GetCurrentMatrix = _bind("GPU_GetCurrentMatrix", None, POINTER(c_float))
GPU_GetModelView = _bind("GPU_GetModelView", None, POINTER(c_float))
GPU_GetProjection = _bind("GPU_GetProjection", None, POINTER(c_float))
GPU_GetModelViewProjection = _bind("GPU_GetModelViewProjection", [POINTER(c_float)], None)

GPU_InitMatrixStack = _bind("GPU_InitMatrixStack", [POINTER(GPU_MatrixStack)], None)
GPU_MatrixMode = _bind("GPU_MatrixMode", [c_int], None)
GPU_PushMatrix = _bind("GPU_PushMatrix", None, None)
GPU_PopMatrix = _bind("GPU_PopMatrix", None, None)
GPU_LoadIdentity = _bind("GPU_LoadIdentity", None, None)
GPU_LoadMatrix = _bind("GPU_LoadMatrix", [POINTER(c_float)], None)
GPU_Ortho = _bind("GPU_Ortho", [c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_Frustum = _bind("GPU_Frustum", [c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_Translate = _bind("GPU_Translate", [c_float, c_float, c_float], None)
GPU_Scale = _bind("GPU_Scale", [c_float, c_float, c_float], None)
GPU_Rotate = _bind("GPU_Rotate", [c_float, c_float, c_float, c_float], None)
GPU_MultMatrix = _bind("GPU_MultMatrix", [POINTER(c_float)], None)

GPU_Clear = _bind("GPU_Clear", [POINTER(GPU_Target)], None)
GPU_ClearColor = _bind("GPU_ClearColor", [POINTER(GPU_Target), SDL_Color], None)
GPU_ClearRGB = _bind("GPU_ClearRGB", [POINTER(GPU_Target), Uint8, Uint8, Uint8], None)
GPU_ClearRGBA = _bind("GPU_ClearRGBA", [POINTER(GPU_Target), Uint8, Uint8, Uint8, Uint8], None)
GPU_Blit = _bind("GPU_Blit", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), c_float, c_float], None)
GPU_BlitRotate = _bind("GPU_BlitRotate", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), c_float, c_float, c_float], None)
GPU_BlitScale = _bind("GPU_BlitScale", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), c_float, c_float, c_float, c_float], None)
GPU_BlitTransform = _bind("GPU_BlitTransform", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float], None)
GPU_BlitTransformX = _bind("GPU_BlitTransformX", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, c_float, c_float], None)
GPU_BlitRect = _bind("GPU_BlitRect", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), POINTER(GPU_Rect)], None)
GPU_BlitRectX = _bind("GPU_BlitRectX", [POINTER(GPU_Image), POINTER(GPU_Rect), POINTER(GPU_Target), POINTER(GPU_Rect), c_float, c_float, c_float, GPU_FlipEnum], None)
GPU_TriangleBatch = _bind("GPU_TriangleBatch", [POINTER(GPU_Image), POINTER(GPU_Target), c_ushort, POINTER(c_float), c_uint, POINTER(c_ushort), GPU_BatchFlagEnum], None)
GPU_TriangleBatchX = _bind("GPU_TriangleBatchX", [POINTER(GPU_Image), POINTER(GPU_Target), c_ushort, c_void_p, c_uint, POINTER(c_ushort), GPU_BatchFlagEnum], None)
GPU_PrimitiveBatch = _bind("GPU_PrimitiveBatch", [POINTER(GPU_Image), POINTER(GPU_Target), GPU_PrimitiveEnum, c_ushort, POINTER(c_float), c_uint, POINTER(c_ushort), GPU_BatchFlagEnum], None)
GPU_PrimitiveBatchV = _bind("GPU_PrimitiveBatchV", [POINTER(GPU_Image), POINTER(GPU_Target), GPU_PrimitiveEnum, c_ushort, c_void_p, c_uint, POINTER(c_ushort), GPU_BatchFlagEnum], None)
GPU_FlushBlitBuffer = _bind("GPU_FlushBlitBuffer", None, None)
GPU_Flip = _bind("GPU_Flip", [POINTER(GPU_Target)], None)

GPU_Pixel = _bind("GPU_Pixel", [POINTER(GPU_Target), c_float, c_float, SDL_Color], None)
GPU_Line = _bind("GPU_Line", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Arc = _bind("GPU_Arc", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_ArcFilled = _bind("GPU_ArcFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Circle = _bind("GPU_Circle", [POINTER(GPU_Target), c_float, c_float, c_float, SDL_Color], None)
GPU_CircleFilled = _bind("GPU_CircleFilled", [POINTER(GPU_Target), c_float, c_float, c_float, SDL_Color], None)
GPU_Ellipse = _bind("GPU_Ellipse", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_EllipseFilled = _bind("GPU_EllipseFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Sector = _bind("GPU_Sector", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_SectorFilled = _bind("GPU_SectorFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Tri = _bind("GPU_Tri", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_TriFilled = _bind("GPU_TriFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Rectangle = _bind("GPU_Rectangle", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_Rectangle2 = _bind("GPU_Rectangle2", [POINTER(GPU_Target), GPU_Rect, SDL_Color], None)
GPU_RectangleFilled = _bind("GPU_RectangleFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_RectangleFilled2 = _bind("GPU_Rectangle2", [POINTER(GPU_Target), GPU_Rect, SDL_Color], None)
GPU_RectangleRound = _bind("GPU_RectangleRound", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_RectangleRound2 = _bind("GPU_RectangleRound2", [POINTER(GPU_Target), GPU_Rect, c_float, SDL_Color], None)
GPU_RectangleRoundFilled = _bind("GPU_RectangleRoundFilled", [POINTER(GPU_Target), c_float, c_float, c_float, c_float, c_float, SDL_Color], None)
GPU_RectangleRoundFilled2 = _bind("GPU_RectangleRoundFilled2", [POINTER(GPU_Target), GPU_Rect, c_float, SDL_Color], None)
GPU_Polygon = _bind("GPU_Polygon", [POINTER(GPU_Target), c_uint, POINTER(c_float), SDL_Color], None)
GPU_PolygonFilled = _bind("GPU_PolygonFilled", [POINTER(GPU_Target), c_uint, POINTER(c_float), SDL_Color], None)

GPU_CreateShaderProgram = _bind("GPU_CreateShaderProgram", None, Uint32)
GPU_FreeShaderProgram = _bind("GPU_FreeShaderProgram", [Uint32], None)
GPU_CompileShader_RW = _bind("GPU_CompileShader_RW", [GPU_ShaderEnum, POINTER(SDL_RWops), GPU_bool], Uint32)
GPU_CompileShader = _bind("GPU_CompileShader", [GPU_ShaderEnum, c_char_p], Uint32)
GPU_LoadShader = _bind("GPU_LoadShader", [GPU_ShaderEnum, c_char_p], Uint32)
GPU_LinkShaders = _bind("GPU_LinkShaders", [Uint32, Uint32], Uint32)
GPU_LinkManyShaders = _bind("GPU_LinkManyShaders", [POINTER(Uint32), c_int], Uint32)
GPU_FreeShader = _bind("GPU_FreeShader", [Uint32], None)
GPU_AttachShader = _bind("GPU_AttachShader", [Uint32, Uint32], None)
GPU_DetachShader = _bind("GPU_DetachShader", [Uint32, Uint32], None)
GPU_LinkShaderProgram = _bind("GPU_LinkShaderProgram", [Uint32], GPU_bool)
GPU_GetCurrentShaderProgram = _bind("GPU_GetCurrentShaderProgram", None, Uint32)
GPU_IsDefaultShaderProgram = _bind("GPU_IsDefaultShaderProgram", [Uint32], GPU_bool)
GPU_ActivateShaderProgram = _bind("GPU_ActivateShaderProgram", [Uint32, GPU_ShaderBlock], None)
GPU_DeactivateShaderProgram = _bind("GPU_DeactivateShaderProgram", None, None)
GPU_GetShaderMessage = _bind("GPU_GetShaderMessage", None, c_char_p)
GPU_GetAttributeLocation = _bind("GPU_GetAttributeLocation", [Uint32, c_char_p], c_int)
GPU_MakeAttributeFormat = _bind("GPU_MakeAttributeFormat", [c_int, GPU_TypeEnum, GPU_bool, c_int, c_int], GPU_AttributeFormat)
GPU_MakeAttribute = _bind("GPU_MakeAttribute", [c_int, c_void_p, GPU_AttributeFormat], GPU_Attribute)
GPU_GetUniformLocation = _bind("GPU_GetUniformLocation", [Uint32, c_char_p], c_int)
GPU_LoadShaderBlock = _bind("GPU_LoadShaderBlock", [Uint32, c_char_p, c_char_p, c_char_p, c_char_p], GPU_ShaderBlock)
GPU_SetShaderBlock = _bind("GPU_SetShaderBlock", [GPU_ShaderBlock], None)
GPU_GetShaderBlock = _bind("GPU_GetShaderBlock", None, GPU_ShaderBlock)
GPU_SetShaderImage = _bind("GPU_SetShaderImage", [POINTER(GPU_Image), c_int, c_int], None)
GPU_GetUniformiv = _bind("GPU_GetUniformiv", [Uint32, c_int, POINTER(c_int)], None)
GPU_SetUniformi = _bind("GPU_SetUniformi", [c_int, c_int], None)
GPU_SetUniformiv = _bind("GPU_SetUniformiv", [c_int, c_int, c_int, POINTER(c_int)], None)
GPU_GetUniformuiv = _bind("GPU_GetUniformuiv", [Uint32, c_int, POINTER(c_uint)], None)
GPU_SetUniformui = _bind("GPU_SetUniformui", [c_int, c_uint], None)
GPU_SetUniformuiv = _bind("GPU_SetUniformuiv", [c_int, c_int, c_int, POINTER(c_int)], None)
GPU_GetUniformfv = _bind("GPU_GetUniformfv", [Uint32, c_int, POINTER(c_float)], None)
GPU_SetUniformf = _bind("GPU_SetUniformf", [c_int, c_float], None)
GPU_SetUniformfv = _bind("GPU_SetUniformfv", [c_int, c_int, c_int, POINTER(c_float)], None)
GPU_GetUniformMatrixfv = _bind("GPU_GetUniformMatrixfv", [Uint32, c_int, POINTER(c_float)], None)
GPU_SetUniformMatrixfv = _bind("GPU_SetUniformMatrixfv", [c_int, c_int, c_int, c_int, GPU_bool, POINTER(c_float)], None)
GPU_SetAttributef = _bind("GPU_SetAttributef", [c_int, c_float], None)
GPU_SetAttributei = _bind("GPU_SetAttributei", [c_int, c_int], None)
GPU_SetAttributeui = _bind("GPU_SetAttributeui", [c_int, c_uint], None)
GPU_SetAttributefv = _bind("GPU_SetAttributefv", [c_int, c_int, POINTER(c_float)], None)
GPU_SetAttributeiv = _bind("GPU_SetAttributeiv", [c_int, c_int, POINTER(c_int)], None)
GPU_SetAttributeuiv = _bind("GPU_SetAttributeuiv", [c_int, c_int, POINTER(c_uint)], None)
GPU_SetAttributeSource = _bind("GPU_SetAttributeSource", [c_int, GPU_Attribute], None)

