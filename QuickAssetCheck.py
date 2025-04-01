import bpy
import bmesh
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


bl_info = {
    "name": "Quick Asset Check",
    "blender": (4, 2, 2),
    "category": "Object",
}

class OBJECT_OT_quick_check(bpy.types.Operator, ImportHelper):
    """Perform a series of transform operations on the selected object"""
    bl_idname = "object.quick_check"
    bl_label = "Quick Asset Check"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    #import setup start
    # ImportHelper mixin class uses this
    filename_ext = ".fbx"
    
    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    exclude_all_collections: BoolProperty(
        name="Exclude All Collections",
        description="Exclude all existing collections from view layer before import",
        default=True,
    )
    #import setup end
    
    
    def execute(self, context):
        # Print status message
        self.report({'INFO'}, "Starting importing")
        print("Transform utility started")
        
        #first, deselect all
        bpy.ops.object.select_all(action='DESELECT')

        #import start
        #Exclude all collections from view layer if option is enabled
        if self.exclude_all_collections:
            for collection in bpy.context.view_layer.layer_collection.children:
                collection.exclude = True
                
        # Get the file path and extract the file name without extension
        filePath = self.filepath
        fileName = os.path.basename(filePath)
        name_without_ext = os.path.splitext(fileName)[0]
        name_without_ext = name_without_ext.split('_')[1]
        
        # 1.Import FBX
        bpy.ops.import_scene.fbx(filepath=filePath)
        # Get the objects that were just imported
        imported_objects = []
        for obj in bpy.context.selected_objects:
            imported_objects.append(obj)
            self.report({'INFO'}, f"obj: {obj.data.name}") 
        # 2.Create a new collection using the file name
        newCollection = bpy.data.collections.new(name_without_ext)
        bpy.context.scene.collection.children.link(newCollection)
        # Make sure the new collection is visible in the view layer
        for collection in bpy.context.view_layer.layer_collection.children:
            if collection.name == name_without_ext:
                collection.exclude = False
        # 3. Move imported objects to the new collection
        for obj in imported_objects:
            # Remove from current collections
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            # Add to new collection
            newCollection.objects.link(obj)

        self.report({'INFO'}, "Import Completed")   
        #import end
        
        
        for obj in imported_objects:
            if obj.type != 'MESH':
                self.report({'INFO'}, f"obj {obj.data.name} is not a mesh, skipping")  
                continue

            #object alignment start
            #after careful thought and various tests, there's no universal object alignment method that fits every assets across static mesh and skeletal mesh
            #Therefore this section is deprecated
            #object alignment end


            #Materail assignment start
            # Create a new material
            self.report({'INFO'}, "Starting assigning material")  
            material_name = f"{obj.name}_Material"
            material = bpy.data.materials.new(name=material_name)
            material.use_nodes = True

            # Clear default nodes
            node_tree = material.node_tree
            nodes = node_tree.nodes
            nodes.clear()
            # Connect nodes
            links = node_tree.links

            # Create Principled BSDF node
            principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            principled_node.location = (300, 0)

            # Create output node
            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (600, 0)
            
            # Connect Principled BSDF to Material Output
            links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])
            
            # Search for matching PNG files in the specified folder
            matchingImages = []
            folderPath = os.path.dirname(filePath)

            if os.path.exists(folderPath) and os.path.isdir(folderPath):
                for file in os.listdir(folderPath):
                    if file.lower().endswith('.png') and file.split('_')[1].lower() == name_without_ext.lower(): 
                        matchingImages.append(os.path.join(folderPath, file))

            
            if not matchingImages:
                self.report({'WARNING'}, "No matching texture found for this asset, please check naming convention, or manually add the corect image")
            
            #if found any images:
            matchingImages.sort()
            textureNodes = [] 
            i = 0
            for path in matchingImages:
                self.report({'INFO'}, f"file name: {path}")
                #load image
                img = bpy.data.images.load(path, check_existing=True)
                #create an image texture for each image found
                textureNode = nodes.new(type='ShaderNodeTexImage')
                textureNode.location = (-300*len(matchingImages), -300 * i)
                textureNode.image = img
                textureNodes.append(textureNode)
                i+=1
            
            if len(textureNodes) == 1: 
                #Connect Image Texture to Principled BSDF Base Color
                links.new(textureNodes[0].outputs["Color"], principled_node.inputs["Base Color"])
            else:
                lastAddNode = None
                for i in range(1, len(textureNodes)):
                    #create a vector add node
                    addNode = nodes.new(type='ShaderNodeVectorMath')
                    addNode.operation = 'ADD'
                    addNode.location = (-300.0 * (len(textureNodes) - i), -300 * (i-1))    

                    #if i == 1, connect textureNodes[0] and textureNodes[1]
                    if i == 1:
                        links.new(textureNodes[0].outputs["Color"], addNode.inputs[0])
                        links.new(textureNodes[1].outputs["Color"], addNode.inputs[1])
                    #else, connect lastAddNode and textureNodes[i]
                    else:
                        links.new(lastAddNode.outputs[0], addNode.inputs[0])
                        links.new(textureNodes[i].outputs["Color"], addNode.inputs[1])

                    lastAddNode = addNode
                links.new(lastAddNode.outputs[0], principled_node.inputs["Base Color"])

            # Assign the material to the active object
            if len(obj.data.materials) == 0:
                obj.data.materials.append(material)
            else:
                obj.data.materials[0] = material

            print(f"Created material with image texture for {obj.name}")
            self.report({'INFO'}, "Material assigned") 
            #Materail assignment end

        return {'FINISHED'}


# Create a custom panel in the N-panel sidebar
class VIEW3D_PT_transform_utility(bpy.types.Panel):
    """Transform Utility Panel"""
    bl_label = "Transform Utility"
    bl_idname = "VIEW3D_PT_transform_utility"
    bl_space_type = 'VIEW_3D'   # Show in the 3D viewport
    bl_region_type = 'UI'       # Shows in the sidebar panel (N)
    bl_category = "Quick Check"   # Tab name in the sidebar
    
    def draw(self, context):
        layout = self.layout
        
        # Create a big button that runs our operator
        row = layout.row()
        row.scale_y = 2.0  # Make the button larger
        row.operator(OBJECT_OT_quick_check.bl_idname, icon='OBJECT_ORIGIN')
        
        # Add some helpful info
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Imports the selected asset")
        col.label(text="Organize the scene by")
        col.label(text="Create material for meshes")
        col.label(text="Brings in textures based on name query")

# Registration
classes = (
    OBJECT_OT_quick_check,
    VIEW3D_PT_transform_utility,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()