import os
import sys
import zlib
import time
import struct


# ===资源类型===
ResourceTypeDict = {"01000000": "Texture",
                    "02000000": "Material",
                    "03000000": "VertexDescriptor",
                    "04000000": "VertexProgramState",
                    "05000000": "Renderable",
                    "06000000": "MaterialState",
                    "07000000": "SamplerState",
                    "08000000": "ShaderProgramBuffer",
                    "10000000": "AttribSysSchema",
                    "11000000": "AttribSysVault",
                    "12000000": "GenesysType",
                    "13000000": "GenesysObject",
                    "14000000": "GenesysType",
                    "15000000": "GenesysObject",
                    "16000000": "BinaryFile",
                    "20000000": "EntryList",
                    "30000000": "Font",
                    "40000000": "LuaCode",
                    "50000000": "InstanceList",
                    "51000000": "Model",
                    "52000000": "ColorCube",
                    "53000000": "Shader",
                    "60000000": "PolygonSoupList",
                    "61000000": "PolygonSoupTree",
                    "68000000": "NavigationMesh",
                    "70000000": "TextFile",
                    "71000000": "TextFile",
                    "72000000": "ResourceHandleList",
                    "74000000": "LuaData",
                    "78000000": "AllocatorInPool",
                    "80000000": "Ginsu",
                    "81000000": "Wave",
                    "82000000": "WaveContainerTable",
                    "83000000": "GameplayLinkData",
                    "84000000": "WaveDictionary",
                    "85000000": "MicroMonoStream",
                    "86000000": "Reverb",
                    "90000000": "ZoneList",
                    "91000000": "WorldPaintMap",
                    "A0000000": "IceAnimDictionary",
                    "B0000000": "AnimationList",
                    "B1000000": "PathAnimation",
                    "B2000000": "Skeleton",
                    "B3000000": "Animation",
                    "C0000000": "CgsVertexProgramState",
                    "C1000000": "CgsProgramBuffer",
                    "DE000000": "DeltaDeleted",
                    "05010000": "VehicleList",
                    "06010000": "GraphicsSpec",
                    "07010000": "VehiclePhysicsSpec",
                    "0A010000": "WheelGraphicsSpec",
                    "12010000": "EnvironmentKeyframe",
                    "13010000": "EnvironmentTimeLine",
                    "14010000": "EnvironmentDictionary",
                    "00020000": "AIData",
                    "01020000": "Language",
                    "02020000": "TriggerData",
                    "03020000": "RoadData",
                    "04020000": "DynamicInstanceList",
                    "05020000": "WorldObject",
                    "06020000": "ZoneHeader",
                    "07020000": "VehicleSound",
                    "08020000": "RoadMapDataResourceType",
                    "09020000": "CharacterSpec",
                    "0A020000": "CharacterList",
                    "0B020000": "SurfaceSounds",
                    "0C020000": "ReverbRoadData",
                    "0D020000": "CameraTake",
                    "0E020000": "CameraTakeList",
                    "0F020000": "GroundcoverCollection",
                    "10020000": "ControlMesh",
                    "11020000": "CutsceneData",
                    "12020000": "CutsceneList",
                    "13020000": "LightInstanceList",
                    "14020000": "GroundcoverInstances",
                    "15020000": "CompoundObject",
                    "16020000": "CompoundInstanceList",
                    "17020000": "PropObject",
                    "18020000": "PropInstanceList",
                    "19020000": "ZoneAmbienceList",
                    "01030000": "BearEffect",
                    "02030000": "BearGlobalParameters",
                    "03030000": "ConvexHull",
                    "01050000": "HSMData",
                    "01070000": "TrafficLaneData"}


def BundlePCUnpacker(Path, Bundle):
    BundleSize = struct.unpack("<L", bytes.fromhex(Bundle[16:24]))[0]
    IDsSize = struct.unpack("<L", bytes.fromhex(Bundle[40:48]))[0]

    ResourceEntriesOffset = struct.unpack("<L", bytes.fromhex(Bundle[32:40]))[0]
    ResourceCompress1Offset = struct.unpack("<L", bytes.fromhex(Bundle[40:48]))[0]
    ResourceCompress2Offset = struct.unpack("<L", bytes.fromhex(Bundle[48:56]))[0]
    ResourceCompress3Offset = struct.unpack("<L", bytes.fromhex(Bundle[56:64]))[0]
    ResourceCompress4Offset = struct.unpack("<L", bytes.fromhex(Bundle[64:72]))[0]

    ResourceCompress1 = Bundle[ResourceCompress1Offset * 2:ResourceCompress2Offset * 2]
    ResourceCompress2 = Bundle[ResourceCompress2Offset * 2:ResourceCompress3Offset * 2]

    ResourceEntireCount = struct.unpack("<L", bytes.fromhex(Bundle[24:32]))[0]
    for ResourceEntireNum in range(ResourceEntireCount):
        ResourceEntrieOffset = ResourceEntriesOffset + ResourceEntireNum * 72
        ResourceEntire = Bundle[ResourceEntrieOffset * 2:(ResourceEntrieOffset + 72) * 2]

        # ===资源条目基本信息===
        ResourceID = ResourceEntire[:8].upper()  # 资源ID(前4位)
        ResourceID = '_'.join([ResourceID[x:x + 2] for x in range(0, len(ResourceID), 2)])  # 资源ID(填充下划线)
        ResourceIDSuffix1 = struct.unpack("<B", bytes.fromhex(ResourceEntire[8:10]))[0]  # 资源ID后缀1
        ResourceIDSuffix2 = struct.unpack("<B", bytes.fromhex(ResourceEntire[12:14]))[0]  # 资源ID后缀2
        if ResourceIDSuffix1 != 0 and ResourceIDSuffix2 != 0:
            ResourceID += "_" + str(ResourceIDSuffix1) + "_" + str(ResourceIDSuffix2)
        elif ResourceIDSuffix1 == 0 and ResourceIDSuffix2 != 0:
            ResourceID += "_0_" + str(ResourceIDSuffix2)
        elif ResourceIDSuffix1 != 0 and ResourceIDSuffix2 == 0:
            ResourceID += "_" + str(ResourceIDSuffix1)

        ResourceTypeID = ResourceEntire[120:128].upper()
        ResourceType = ResourceTypeDict[ResourceTypeID]

        OutputDirPath = os.path.dirname(Path) + "\\" + os.path.basename(Path).replace(".BNDL", "") + "\\" + ResourceType
        if not os.path.exists(OutputDirPath):
            os.makedirs(OutputDirPath)

        ResourceCompress1BlockOffset = struct.unpack("<L", bytes.fromhex(ResourceEntire[80:88]))[0]
        ResourceCompress1BlockSize = struct.unpack("<L", bytes.fromhex(ResourceEntire[48:56]))[0]

        ResourceCompress1Block = ResourceCompress1[ResourceCompress1BlockOffset * 2:(ResourceCompress1BlockOffset + ResourceCompress1BlockSize) * 2]
        ResourceUnCompress1Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress1Block)).hex()  # 解压压缩资源数据1

        Unpack = open(OutputDirPath + "\\" + ResourceID + ".dat", "wb")
        Unpack.write(bytes.fromhex(ResourceUnCompress1Block))
        Unpack.close()

        if ResourceType == "Texture":
            ResourceCompress2BlockOffset = struct.unpack("<L", bytes.fromhex(ResourceEntire[88:96]))[0]
            ResourceCompress2BlockSize = struct.unpack("<L", bytes.fromhex(ResourceEntire[56:64]))[0]

            ResourceCompress2Block = ResourceCompress2[ResourceCompress2BlockOffset * 2:(ResourceCompress2BlockOffset + ResourceCompress2BlockSize) * 2]
            ResourceUnCompress2Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress2Block)).hex()  # 解压压缩资源数据1

            Unpack = open(OutputDirPath + "\\" + ResourceID + "_texture.dat", "wb")
            Unpack.write(bytes.fromhex(ResourceUnCompress2Block))
            Unpack.close()

        elif ResourceType == "Renderable":
            ResourceCompress2BlockOffset = struct.unpack("<L", bytes.fromhex(ResourceEntire[88:96]))[0]
            ResourceCompress2BlockSize = struct.unpack("<L", bytes.fromhex(ResourceEntire[56:64]))[0]

            ResourceCompress2Block = ResourceCompress2[ResourceCompress2BlockOffset * 2:(ResourceCompress2BlockOffset + ResourceCompress2BlockSize) * 2]
            ResourceUnCompress2Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress2Block)).hex()  # 解压压缩资源数据1

            Unpack = open(OutputDirPath + "\\" + ResourceID + "_model.dat", "wb")
            Unpack.write(bytes.fromhex(ResourceUnCompress2Block))
            Unpack.close()

    IDs = open(os.path.dirname(OutputDirPath) + "\\" + "IDs.BIN", "wb")
    IDs.write(bytes.fromhex(Bundle[:IDsSize * 2]))
    IDs.close()

    # ===Debug信息===
    if BundleSize != len(Bundle) // 2:
            DebugXml = open(os.path.dirname(OutputDirPath) + "\\" + "ResourceStringTable.xml", "wb")
            DebugXml.write(bytes.fromhex(Bundle[BundleSize * 2:]))
            DebugXml.close()


def BundlePS3Unpacker(Path, Bundle):
    BundleSize =  struct.unpack(">L", bytes.fromhex(Bundle[16:24]))[0]
    IDsSize = struct.unpack(">L", bytes.fromhex(Bundle[40:48]))[0]

    ResourceEntriesOffset = struct.unpack(">L", bytes.fromhex(Bundle[32:40]))[0]
    ResourceCompress1Offset = struct.unpack(">L", bytes.fromhex(Bundle[40:48]))[0]
    ResourceCompress2Offset = struct.unpack(">L", bytes.fromhex(Bundle[48:56]))[0]
    ResourceCompress3Offset = struct.unpack(">L", bytes.fromhex(Bundle[56:64]))[0]
    ResourceCompress4Offset = struct.unpack(">L", bytes.fromhex(Bundle[64:72]))[0]

    ResourceCompress1 = Bundle[ResourceCompress1Offset * 2:ResourceCompress2Offset * 2]
    ResourceCompress2 = Bundle[ResourceCompress2Offset * 2:ResourceCompress3Offset * 2]
    ResourceCompress3 = Bundle[ResourceCompress3Offset * 2:ResourceCompress4Offset * 2]
    ResourceCompress4 = Bundle[ResourceCompress4Offset * 2:BundleSize * 2]

    ResourceEntireCount = struct.unpack(">L", bytes.fromhex(Bundle[24:32]))[0]
    for ResourceEntireNum in range(ResourceEntireCount):
        ResourceEntrieOffset = ResourceEntriesOffset + ResourceEntireNum * 72
        ResourceEntire = Bundle[ResourceEntrieOffset * 2:(ResourceEntrieOffset + 72) * 2]

        # ===资源条目基本信息===
        ResourceID = ResourceEntire[8:16].upper()  # 资源ID(前4位)
        ResourceID = '_'.join([ResourceID[x:x + 2] for x in range(0, len(ResourceID), 2)])  # 资源ID(填充下划线)
        ResourceIDSuffix1 = struct.unpack(">B", bytes.fromhex(ResourceEntire[2:4]))[0]  # 资源ID后缀1
        ResourceIDSuffix2 = struct.unpack(">B", bytes.fromhex(ResourceEntire[6:8]))[0]  # 资源ID后缀2
        if ResourceIDSuffix2 != 0 and ResourceIDSuffix1 != 0:
            ResourceID += "_" + str(ResourceIDSuffix2) + "_" + str(ResourceIDSuffix1)
        elif ResourceIDSuffix2 == 0 and ResourceIDSuffix1 != 0:
            ResourceID += "_0_" + str(ResourceIDSuffix1)
        elif ResourceIDSuffix2 != 0 and ResourceIDSuffix1 == 0:
            ResourceID += "_" + str(ResourceIDSuffix2)

        ResourceTypeID = ResourceEntire[120:128].upper()
        ResourceTypeID = ResourceTypeID[6:8] + ResourceTypeID[4:6] + ResourceTypeID[2:4] + ResourceTypeID[:2]
        ResourceType = ResourceTypeDict[ResourceTypeID]

        OutputDirPath = os.path.dirname(Path) + "\\" + os.path.basename(Path).replace(".BNDL", "") + "\\" + ResourceType
        if not os.path.exists(OutputDirPath):
            os.makedirs(OutputDirPath)

        ResourceCompress1BlockOffset = struct.unpack(">L", bytes.fromhex(ResourceEntire[80:88]))[0]
        ResourceCompress1BlockSize = struct.unpack(">L", bytes.fromhex(ResourceEntire[48:56]))[0]

        ResourceCompress1Block = ResourceCompress1[ResourceCompress1BlockOffset * 2:(ResourceCompress1BlockOffset + ResourceCompress1BlockSize) * 2]
        ResourceUnCompress1Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress1Block)).hex()  # 解压压缩资源数据1

        UnpackedResource = open(OutputDirPath + "\\" + ResourceID + ".dat", "wb")
        UnpackedResource.write(bytes.fromhex(ResourceUnCompress1Block))
        UnpackedResource.close()

        if ResourceType == "ShaderProgramBuffer":
            ResourceCompress2BlockOffset = struct.unpack(">L", bytes.fromhex(ResourceEntire[88:96]))[0]
            ResourceCompress2BlockSize = struct.unpack(">L", bytes.fromhex(ResourceEntire[56:64]))[0]

            ResourceCompress2Block = ResourceCompress2[ResourceCompress2BlockOffset * 2:(ResourceCompress2BlockOffset + ResourceCompress2BlockSize) * 2]
            ResourceUnCompress2Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress2Block)).hex()  # 解压压缩资源数据1

            UnpackedResource = open(OutputDirPath + "\\" + ResourceID + "_unknow.dat", "wb")
            UnpackedResource.write(bytes.fromhex(ResourceUnCompress2Block))
            UnpackedResource.close()

        elif ResourceType == "Texture":
            ResourceCompress3BlockOffset = struct.unpack(">L", bytes.fromhex(ResourceEntire[96:104]))[0]
            ResourceCompress3BlockSize = struct.unpack(">L", bytes.fromhex(ResourceEntire[64:72]))[0]

            ResourceCompress3Block = ResourceCompress3[ResourceCompress3BlockOffset * 2:(ResourceCompress3BlockOffset + ResourceCompress3BlockSize) * 2]
            ResourceUnCompress3Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress3Block)).hex()  # 解压压缩资源数据1

            UnpackedResource = open(OutputDirPath + "\\" + ResourceID + "_texture.dat", "wb")
            UnpackedResource.write(bytes.fromhex(ResourceUnCompress3Block))
            UnpackedResource.close()

        elif ResourceType == "Renderable":
            ResourceCompress3BlockOffset = struct.unpack(">L", bytes.fromhex(ResourceEntire[96:104]))[0]
            ResourceCompress3BlockSize = struct.unpack(">L", bytes.fromhex(ResourceEntire[64:72]))[0]

            ResourceCompress3Block = ResourceCompress3[ResourceCompress3BlockOffset * 2:(ResourceCompress3BlockOffset + ResourceCompress3BlockSize) * 2]
            ResourceUnCompress3Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress3Block)).hex()  # 解压压缩资源数据1

            UnpackedResource = open(OutputDirPath + "\\" + ResourceID + "_vertices.dat", "wb")
            UnpackedResource.write(bytes.fromhex(ResourceUnCompress3Block))
            UnpackedResource.close()

        elif ResourceType == "CgsProgramBuffer":
            ResourceCompress4BlockOffset = struct.unpack(">L", bytes.fromhex(ResourceEntire[104:112]))[0]
            ResourceCompress4BlockSize = struct.unpack(">L", bytes.fromhex(ResourceEntire[72:80]))[0]

            ResourceCompress4Block = ResourceCompress4[ResourceCompress4BlockOffset * 2:(ResourceCompress4BlockOffset + ResourceCompress4BlockSize) * 2]
            ResourceUnCompress4Block = zlib.decompressobj().decompress(bytes.fromhex(ResourceCompress4Block)).hex()  # 解压压缩资源数据1

            UnpackedResource = open(OutputDirPath + "\\" + ResourceID + "_unknow.dat", "wb")
            UnpackedResource.write(bytes.fromhex(ResourceUnCompress4Block))
            UnpackedResource.close()

    IDs = open(os.path.dirname(OutputDirPath) + "\\" + "IDs.BIN", "wb")
    IDs.write(bytes.fromhex(Bundle[:IDsSize * 2]))
    IDs.close()

    # ===Debug信息===
    if BundleSize != len(Bundle) // 2:
            DebugXml = open(os.path.dirname(OutputDirPath) + "\\" + "ResourceStringTable.xml", "wb")
            DebugXml.write(bytes.fromhex(Bundle[BundleSize * 2:]))
            DebugXml.close()


def BundlePCPacker(Path, IDs):
    NewResourceEntiresChunk = str()
    NewResourceCompressedChunk1 = str()
    NewResourceCompressedChunk2 = str()
    ResourceCompressed1Offset = int()
    ResourceCompressed2Offset = int()

    NewIDsSize = len(IDs) // 2
    NewResourceEntrieCount = (NewIDsSize - 112) // 72  # 重新计算资源条目数量
    ResourceEntriesOffset = struct.unpack("<L", bytes.fromhex(IDs[32:40]))[0]

    for ResourceEntrieNum in range(NewResourceEntrieCount):
        ResourceEntrie = IDs[(ResourceEntriesOffset + 72 * ResourceEntrieNum) * 2:(ResourceEntriesOffset + 72 * (ResourceEntrieNum + 1)) * 2]

        ResourceID = ResourceEntrie[:8].upper()
        ResourceID = '_'.join([ResourceID[x:x + 2] for x in range(0, len(ResourceID), 2)])
        ResourceIdSuffix1 = struct.unpack("<B", bytes.fromhex(ResourceEntrie[8:10]))[0]
        ResourceIdSuffix2 = struct.unpack("<B", bytes.fromhex(ResourceEntrie[12:14]))[0]
        if ResourceIdSuffix1 != 0 and ResourceIdSuffix2 != 0:
            ResourceID += "_" + str(ResourceIdSuffix1) + "_" + str(ResourceIdSuffix2)
        elif ResourceIdSuffix1 == 0 and ResourceIdSuffix2 != 0:
            ResourceID += "_0_" + str(ResourceIdSuffix2)
        elif ResourceIdSuffix1 != 0 and ResourceIdSuffix2 == 0:
            ResourceID += "_" + str(ResourceIdSuffix1)

        ResourceTypeID = ResourceEntrie[120:128].upper()
        ResourceType = '_'.join([ResourceTypeID[x:x + 2] for x in range(0, len(ResourceTypeID), 2)])
        try:
            ResourceType = ResourceTypeDict[ResourceTypeID]
        except:
            input("Error:Unrecognized data type[{}]".format(ResourceType))
            continue

        if ResourceType == "BearEffect":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportCount = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[8:10]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "CompoundInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportCount = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "CompoundObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                CompoundObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if CompoundObjectData == "0400000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "CharacterSpec":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportCount = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[32:36]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "DynamicInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportCount = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "Font":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[8:16]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "GenesysType":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            GenesysType1 = struct.unpack("<B", bytes.fromhex(ResourceUncompressed1[2:4]))[0]
            GenesysType2 = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[4:8]))[0]
            if GenesysType1 == 7 and GenesysType2 != 0:
                ImportCount = GenesysType2 + 1
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16
            elif GenesysType1 == 6:
                ImportCount = GenesysType2
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16
            else:
                ImportCount = ImportsOffset = 0

        elif ResourceType == "GenesysObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                GenesysObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if GenesysObjectData == "0000008000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "GraphicsSpec":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[1232:1240]))[0] + 16
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "GroundcoverCollection":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = 0
            ImportCount = 0
            for i in range(ResourceUncompressed1Size // 8):
                GenesysObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if GenesysObjectData == "4000008000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "InstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                InstanceListData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if InstanceListData == "1000000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "Material":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[12:16]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "Model":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            AttributeCode = ResourceUncompressed1[:8] + "00000000"
            for i in range(ResourceUncompressed1Size // 8):
                ModelData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if ModelData == AttributeCode:  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "PropInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportCount = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "PropObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                PropObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if PropObjectData == "0400000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "Renderable":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            Resource2Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_model.dat"
            ResourceUncompressed2 = open(Resource2Path, "rb").read().hex()
            ResourceUncompressed2Size = len(ResourceUncompressed2) // 2

            ResourceCompressed2 = zlib.compress(bytes.fromhex(ResourceUncompressed2), 9).hex()
            ResourceCompressed2Size = len(ResourceCompressed2) // 2
            NewResourceCompressedChunk2 += ResourceCompressed2

            ImportCount = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[36:40]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "Shader":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = struct.unpack("<H", bytes.fromhex(ResourceUncompressed1[36:40]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "Texture":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            Resource2Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_texture.dat"
            ResourceUncompressed2 = open(Resource2Path, "rb").read().hex()
            ResourceUncompressed2Size = len(ResourceUncompressed2) // 2

            ResourceCompressed2 = zlib.compress(bytes.fromhex(ResourceUncompressed2), 9).hex()
            ResourceCompressed2Size = len(ResourceCompressed2) // 2
            NewResourceCompressedChunk2 += ResourceCompressed2

            ImportsOffset = 0
            ImportCount = 0

        elif ResourceType == "TrafficLaneData":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = struct.unpack("<L", bytes.fromhex(ResourceUncompressed1[8:16]))[0] + 8
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "VehicleSound":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                VehicleSoundData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if VehicleSoundData == "1000008000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "VertexProgramState":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                VertexProgramStateData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if VertexProgramStateData == "0400000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "WorldObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                WorldObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if WorldObjectData == "0400000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "ZoneHeader":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                ZoneHeaderData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if ZoneHeaderData == "0400008000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        else:
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ImportsOffset = 0
            ImportCount = 0

        if ResourceUncompressed2Size != 0 and ResourceCompressed2Size != 0:
            NewResourceEntrie = ResourceEntrie[:16] + struct.pack("<L", ResourceUncompressed1Size).hex()[:6] + ResourceEntrie[22:24] + struct.pack("<L", ResourceUncompressed2Size).hex()[:6] + ResourceEntrie[30:48] + struct.pack("<L", ResourceCompressed1Size).hex() + struct.pack("<L", ResourceCompressed2Size).hex() + ResourceEntrie[64:80] + struct.pack("<L", ResourceCompressed1Offset).hex() + struct.pack("<L", ResourceCompressed2Offset).hex() + ResourceEntrie[96:112] + struct.pack("<L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack("<H", ImportCount).hex() + ResourceEntrie[132:]
        else:
            NewResourceEntrie = ResourceEntrie[:16] + struct.pack("<L", ResourceUncompressed1Size).hex()[:6] + ResourceEntrie[22:48] + struct.pack("<L", ResourceCompressed1Size).hex() + struct.pack("<L", ResourceCompressed2Size).hex() + ResourceEntrie[64:80] + struct.pack("<L", ResourceCompressed1Offset).hex() + ResourceEntrie[88:112] + struct.pack("<L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack("<H", ImportCount).hex() + ResourceEntrie[132:]

        NewResourceEntiresChunk += NewResourceEntrie
        ResourceCompressed1Offset += ResourceCompressed1Size
        ResourceCompressed2Offset += ResourceCompressed2Size

    NewBundleSize = NewIDsSize + ResourceCompressed1Offset + ResourceCompressed2Offset
    ResourceCompressed2ChunkOffset = NewIDsSize + ResourceCompressed1Offset
    NewIDsHeader = IDs[:16] + struct.pack("<L", NewBundleSize).hex() + struct.pack("<L", NewResourceEntrieCount).hex() + IDs[32:40] + struct.pack("<L", NewIDsSize).hex() + struct.pack("<L", ResourceCompressed2ChunkOffset).hex() + struct.pack("<L", NewBundleSize).hex() * 2 + IDs[72:224]

    DebugInfoXmlPath = Path + "\\" + "ResourceStringTable.xml"
    if os.path.exists(DebugInfoXmlPath):
        DebugInfo = open(DebugInfoXmlPath, "rb").read().hex()
    else:
        DebugInfo = str()

    NewBundleOutputPath = Path + ".BNDL"
    NewBundle = open(NewBundleOutputPath, "wb")
    NewBundle.write(bytes.fromhex(NewIDsHeader + NewResourceEntiresChunk + NewResourceCompressedChunk1 + NewResourceCompressedChunk2 + DebugInfo))
    NewBundle.close()


def BundlePS3Packer(Path, IDs):
    NewResourceEntiresChunk = str()
    NewResourceCompressedChunk1 = str()
    NewResourceCompressedChunk2 = str()
    NewResourceCompressedChunk3 = str()
    NewResourceCompressedChunk4 = str()
    ResourceCompressed1Offset = int()
    ResourceCompressed2Offset = int()
    ResourceCompressed3Offset = int()
    ResourceCompressed4Offset = int()

    NewIDsSize = len(IDs) // 2
    NewResourceEntrieCount = (NewIDsSize - 112) // 72  # 重新计算资源条目数量
    ResourceEntriesOffset = struct.unpack(">L", bytes.fromhex(IDs[32:40]))[0]

    for ResourceEntrieNum in range(NewResourceEntrieCount):
        ResourceEntrie = IDs[(ResourceEntriesOffset + 72 * ResourceEntrieNum) * 2:(ResourceEntriesOffset + 72 * (ResourceEntrieNum + 1)) * 2]

        ResourceID = ResourceEntrie[8:16].upper()
        ResourceID = '_'.join([ResourceID[x:x + 2] for x in range(0, len(ResourceID), 2)])
        ResourceIDSuffix1 = struct.unpack(">B", bytes.fromhex(ResourceEntrie[2:4]))[0]
        ResourceIDSuffix2 = struct.unpack(">B", bytes.fromhex(ResourceEntrie[6:8]))[0]
        if ResourceIDSuffix2 != 0 and ResourceIDSuffix1 != 0:
            ResourceID += "_" + str(ResourceIDSuffix2) + "_" + str(ResourceIDSuffix1)
        elif ResourceIDSuffix2 == 0 and ResourceIDSuffix1 != 0:
            ResourceID += "_0_" + str(ResourceIDSuffix1)
        elif ResourceIDSuffix2 != 0 and ResourceIDSuffix1 == 0:
            ResourceID += "_" + str(ResourceIDSuffix2)

        ResourceTypeID = ResourceEntrie[120:128].upper()
        ResourceTypeID = ResourceTypeID[6:] + ResourceTypeID[4:6] + ResourceTypeID[2:4] + ResourceTypeID[:2]
        ResourceType = '_'.join([ResourceTypeID[x:x + 2] for x in range(0, len(ResourceTypeID), 2)])
        try:
            ResourceType = ResourceTypeDict[ResourceTypeID]
        except:
            input("Error:Unrecognized data type[{}]".format(ResourceType))
            continue

        if ResourceType == "BearEffect":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportCount = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[8:10]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "CgsVertexProgramState":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportCount = 2
            ImportsOffset = 16

        elif ResourceType == "CgsProgramBuffer":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            Resource4Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_unknow.dat"
            ResourceUncompressed4 = open(Resource4Path, "rb").read().hex()
            ResourceUncompressed4Size = len(ResourceUncompressed4) // 2

            ResourceCompressed4 = zlib.compress(bytes.fromhex(ResourceUncompressed4), 9).hex()
            ResourceCompressed4Size = len(ResourceCompressed4) // 2
            NewResourceCompressedChunk4 += ResourceCompressed4

            ImportCount = 0
            ImportsOffset = 0

        elif ResourceType == "CompoundInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            if ResourceUncompressed1Size == 16:
                ImportsOffset = 0
                ImportCount = 0
            else:
                ImportCount = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "CompoundObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                CompoundObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if CompoundObjectData == "0800000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "CharacterSpec":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportCount = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[32:36]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "DynamicInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            if ResourceUncompressed1Size == 16:
                ImportsOffset = 0
                ImportCount = 0
            else:
                ImportCount = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "Font":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[8:16]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "GenesysType":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            GenesysType1 = struct.unpack(">B", bytes.fromhex(ResourceUncompressed1[2:4]))[0]
            GenesysType2 = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[4:8]))[0]
            if GenesysType1 == 7 and GenesysType2 != 0:
                ImportCount = GenesysType2 + 1
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16
            elif GenesysType1 == 6:
                ImportCount = GenesysType2
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16
            else:
                ImportCount = ImportsOffset = 0

        elif ResourceType == "GenesysObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                GenesysObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if GenesysObjectData == "8000000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "GraphicsSpec":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[608:616]))[0] + 32
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "GroundcoverCollection":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                GenesysObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if GenesysObjectData == "8000004000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break
                else:
                    ImportsOffset = 0
                    ImportCount = 0

        elif ResourceType == "InstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                InstanceListData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if InstanceListData == "0000001000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "Material":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[12:16]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "Model":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            AttributeCode = ResourceUncompressed1[:8] + "00000000"
            for i in range(ResourceUncompressed1Size // 8):
                ModelData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if ModelData == AttributeCode:  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "PropInstanceList":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            if ResourceUncompressed1Size == 16:
                ImportsOffset = 0
                ImportCount = 0
            else:
                ImportCount = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[16:24]))[0]
                ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "PropObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                PropObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if PropObjectData == "0000000400000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "Renderable":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            Resource3Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_vertices.dat"
            ResourceUncompressed3 = open(Resource3Path, "rb").read().hex()
            ResourceUncompressed3Size = len(ResourceUncompressed3) // 2

            ResourceCompressed3 = zlib.compress(bytes.fromhex(ResourceUncompressed3), 9).hex()
            ResourceCompressed3Size = len(ResourceCompressed3) // 2
            NewResourceCompressedChunk3 += ResourceCompressed3

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportCount = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[36:40]))[0]
            ImportsOffset = ResourceUncompressed1Size - ImportCount * 16

        elif ResourceType == "Shader":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = struct.unpack(">H", bytes.fromhex(ResourceUncompressed1[36:40]))[0]
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "ShaderProgramBuffer":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            Resource2Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_unknow.dat"
            ResourceUncompressed2 = open(Resource2Path, "rb").read().hex()
            ResourceUncompressed2Size = len(ResourceUncompressed2) // 2

            ResourceCompressed2 = zlib.compress(bytes.fromhex(ResourceUncompressed2), 9).hex()
            ResourceCompressed2Size = len(ResourceCompressed2) // 2
            NewResourceCompressedChunk2 += ResourceCompressed2

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = 0
            ImportCount = 0

        elif ResourceType == "Texture":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            Resource3Path = Path + "\\" + ResourceType + "\\" + ResourceID + "_texture.dat"
            ResourceUncompressed3 = open(Resource3Path, "rb").read().hex()
            ResourceUncompressed3Size = len(ResourceUncompressed3) // 2

            ResourceCompressed3 = zlib.compress(bytes.fromhex(ResourceUncompressed3), 9).hex()
            ResourceCompressed3Size = len(ResourceCompressed3) // 2
            NewResourceCompressedChunk3 += ResourceCompressed3

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = 0
            ImportCount = 0

        elif ResourceType == "TrafficLaneData":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = struct.unpack(">L", bytes.fromhex(ResourceUncompressed1[8:16]))[0] + 8
            ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16

        elif ResourceType == "VehicleSound":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                VehicleSoundData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if VehicleSoundData == "8000000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "VertexProgramState":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                VertexProgramStateData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if VertexProgramStateData == "4000000000000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "WorldObject":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                WorldObjectData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if WorldObjectData == "8000001C00000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        elif ResourceType == "ZoneHeader":
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            for i in range(ResourceUncompressed1Size // 8):
                ZoneHeaderData = ResourceUncompressed1[i * 16:(i + 1) * 16]
                if ZoneHeaderData == "8000000400000000":  # 特征码搜索
                    ImportsOffset = (i - 1) * 8  # 导入表偏移
                    ImportCount = (ResourceUncompressed1Size - ImportsOffset) // 16
                    break

        else:
            Resource1Path = Path + "\\" + ResourceType + "\\" + ResourceID + ".dat"
            ResourceUncompressed1 = open(Resource1Path, "rb").read().hex()
            ResourceUncompressed1Size = len(ResourceUncompressed1) // 2

            ResourceCompressed1 = zlib.compress(bytes.fromhex(ResourceUncompressed1), 9).hex()
            ResourceCompressed1Size = len(ResourceCompressed1) // 2
            NewResourceCompressedChunk1 += ResourceCompressed1

            ResourceUncompressed2Size = 0
            ResourceCompressed2Size = 0

            ResourceUncompressed3Size = 0
            ResourceCompressed3Size = 0

            ResourceUncompressed4Size = 0
            ResourceCompressed4Size = 0

            ImportsOffset = 0
            ImportCount = 0

        if ResourceUncompressed4Size != 0 and ResourceCompressed4Size != 0:
            NewResourceEntrie = ResourceEntrie[:18] + struct.pack(">L", ResourceUncompressed1Size).hex()[2:] + ResourceEntrie[24:42] + struct.pack(">L", ResourceUncompressed4Size).hex()[2:] + struct.pack(">L", ResourceCompressed1Size).hex() + ResourceEntrie[56:72] + struct.pack(">L", ResourceCompressed4Size).hex() + struct.pack(">L", ResourceCompressed1Offset).hex() + ResourceEntrie[88:104] + struct.pack(">L", ResourceCompressed4Offset).hex() + struct.pack(">L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack(">H", ImportCount).hex() + ResourceEntrie[132:]
        elif ResourceUncompressed3Size != 0 and ResourceCompressed3Size != 0:
            NewResourceEntrie = ResourceEntrie[:18] + struct.pack(">L", ResourceUncompressed1Size).hex()[2:] + ResourceEntrie[24:34] + struct.pack(">L", ResourceUncompressed3Size).hex()[2:] + ResourceEntrie[40:48] + struct.pack(">L", ResourceCompressed1Size).hex() + ResourceEntrie[56:64]  + struct.pack(">L", ResourceCompressed3Size).hex() + ResourceEntrie[72:80] + struct.pack(">L", ResourceCompressed1Offset).hex() + ResourceEntrie[88:96] + struct.pack(">L", ResourceCompressed3Offset).hex() + ResourceEntrie[104:112] + struct.pack(">L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack(">H", ImportCount).hex() + ResourceEntrie[132:]
        elif ResourceUncompressed2Size != 0 and ResourceCompressed2Size != 0:
            NewResourceEntrie = ResourceEntrie[:18] + struct.pack(">L", ResourceUncompressed1Size).hex()[2:] + ResourceEntrie[24:26] + struct.pack(">L", ResourceUncompressed2Size).hex()[2:] + ResourceEntrie[32:48] + struct.pack(">L", ResourceCompressed1Size).hex() + struct.pack(">L", ResourceCompressed2Size).hex() + ResourceEntrie[64:80] + struct.pack(">L", ResourceCompressed1Offset).hex() + struct.pack(">L", ResourceCompressed2Offset).hex() + ResourceEntrie[96:112] + struct.pack(">L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack(">H", ImportCount).hex() + ResourceEntrie[132:]
        else:
            NewResourceEntrie = ResourceEntrie[:18] + struct.pack(">L", ResourceUncompressed1Size).hex()[2:] + ResourceEntrie[24:48] + struct.pack(">L", ResourceCompressed1Size).hex() + ResourceEntrie[56:80] + struct.pack(">L", ResourceCompressed1Offset).hex() + ResourceEntrie[88:112] + struct.pack(">L", ImportsOffset).hex() + ResourceEntrie[120:128] + struct.pack(">H", ImportCount).hex() + ResourceEntrie[132:]

        NewResourceEntiresChunk += NewResourceEntrie
        ResourceCompressed1Offset += ResourceCompressed1Size
        ResourceCompressed2Offset += ResourceCompressed2Size
        ResourceCompressed3Offset += ResourceCompressed3Size
        ResourceCompressed4Offset += ResourceCompressed4Size

    NewBundleSize = NewIDsSize + ResourceCompressed1Offset + ResourceCompressed2Offset + ResourceCompressed3Offset + ResourceCompressed4Offset
    ResourceCompressed2ChunkOffset = NewIDsSize + ResourceCompressed1Offset
    NewIDsHeader = IDs[:16] + struct.pack(">L", NewBundleSize).hex() + struct.pack(">L", NewResourceEntrieCount).hex() + IDs[32:40] + struct.pack(">L", NewIDsSize).hex() + struct.pack(">L", ResourceCompressed2ChunkOffset).hex() * 2 + struct.pack(">L", NewBundleSize).hex() + IDs[72:224]

    DebugInfoXmlPath = Path + "\\" + "ResourceStringTable.xml"
    if os.path.exists(DebugInfoXmlPath):
        DebugInfo = open(DebugInfoXmlPath, "rb").read().hex()
    else:
        DebugInfo = str()

    NewBundleOutputPath = Path + ".BNDL"
    NewBundle = open(NewBundleOutputPath, "wb")
    NewBundle.write(bytes.fromhex(NewIDsHeader + NewResourceEntiresChunk + NewResourceCompressedChunk1 + NewResourceCompressedChunk2 + NewResourceCompressedChunk3 + NewResourceCompressedChunk4 + DebugInfo))
    NewBundle.close()


print("Need For Speed Most Wanted(2012) Bundle Tool By NIVSAYZ")
print("Version:1.0.0")
PathList = sys.argv[1:]
for Path in PathList:
    if "." in Path:
        Bundle = open(Path, "rb").read().hex()
        MagicNumber = Bundle[:8]
        if MagicNumber != "626e6432":
            input("Error:This bundle is not in bnd2 format[{}]".format(os.path.basename(Path)))
            continue

        PlatformCode = Bundle[12:16]
        if PlatformCode == "0100":  # PC
            BundlePCUnpacker(Path, Bundle)
        elif PlatformCode == "0002":  # PS3
            BundlePS3Unpacker(Path, Bundle)
        else:
            input("Error:Unknown platform[{}]".format(os.path.basename(Path)))
            continue

    else:
        IDsPath = Path + "\\" + "IDs.BIN"
        IDs = open(IDsPath, "rb").read().hex()

        PlatformCode = IDs[12:16]
        if PlatformCode == "0100":  # PC
            BundlePCPacker(Path, IDs)
        elif PlatformCode == "0002":  # PS3
            BundlePS3Packer(Path, IDs)
        else:
            input("Error:Unknown platform[{}]".format(os.path.basename(Path)))
            continue
print("Completed!")
time.sleep(2)
exit()
