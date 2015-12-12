import bpy
import bmesh
from math import pi,sin,sqrt,radians,degrees
from mathutils import Vector

bl_info = {
	"name": "Circles",
	"author": "Juha Wiiala (TynkaTopi), Oren Titane (Genome36)",
	"version": (0, 2, 0),
	"blender": (2, 72, 0),
	"location": "Object",
	"description": "Create circles using a selected object and an array modifier",
	"warning": "beta",
	"wiki_url": "",
	"category": "",	
}


class Create(bpy.types.Operator):
	bl_idname = "wm.create_spiral"
	bl_label = "Create spiral"
	bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
	
	corners = bpy.props.IntProperty(
		name = "Corners",
		description = "Number of object in array",
		default = 3,
		min = 2,
		step = 1
		)
	activeobject = bpy.props.StringProperty()
	
	def print_vert_details(self, context):
	
		#o = bpy.context.scene.objects.active
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		o = bpy.data.objects[self.active_obj_name]
		
		if o.type == 'MESH':
			#mesh vertices coord
			vertices = o.data.polygons.data.vertices
			vco = [vert.co for vert in vertices if vert.select]

		elif o.type == 'CURVE':
			spline = o.data.splines[0]
			if spline.type in ('NURBS', 'POLY'):
				vco = [p.co for x in o.data.splines for p in x.points if p.select]
			else:
				#curve bezier point coord
				vco = [p.co for x in o.data.splines for p in x.bezier_points if p.select_control_point]
		
		if len(vco) == 2:
			
			wmtx = o.matrix_world
			vco =  [wmtx * x for x in vco]
			
			#smallest vert.x is first in the list, left vertex
			vco = sorted(vco, key = lambda vco: vco[0])
			
			diffx = vco[0][0] - vco[1][0]
			diffy = vco[0][1] - vco[1][1]
			middlex = (vco[0][0] + vco[1][0]) / 2 
			#print ("middlex=", middlex)
			#corners = 12
			corners = self.corners
			#print ("corners:",corners)
			
			distcorner = abs(diffx / sin(pi/corners)/2)
			distmiddle = sqrt(distcorner**2 - ((diffx/2)**2))
			
			bpy.context.scene.cursor_location = ( middlex , vco[0][1] + distmiddle , vco[0][2])
			#print ("diffy", diffy)

			o.select = True
			context.scene.objects.active = o
			obj = bpy.ops.object
			obj.origin_set(type='ORIGIN_CURSOR')
			#add an empty object
			empty = bpy.data.objects.new("empty", None)
			emptyname = empty.name
			#print ("emptyname=",emptyname)
			empty.location = bpy.context.scene.cursor_location
			empty.location.y -= diffy
			bpy.context.scene.objects.link(empty)

			bpy.context.scene.update()

			#plane = bpy.context.scene.objects.active
			bpy.ops.object.select_all(action='DESELECT')

			bpy.context.scene.objects.active = empty
			empty.select = True

			rotation = abs(radians(360/corners))
			#print ("rotation:",rotation)
			if diffy < 0:
				rotation = abs(rotation)
				#print ("diffy >= 0, rotation:", rotation)
			
			bpy.ops.transform.rotate(value= rotation, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
			
			
			bpy.ops.object.select_all(action='DESELECT')
			o.select = True
			context.scene.objects.active = o
			
			obj = bpy.ops.object
			obj.modifier_add(type= 'ARRAY')
			bpy.context.object.modifiers["Array"].use_relative_offset = False
			bpy.context.object.modifiers["Array"].use_object_offset = True
			bpy.context.object.modifiers["Array"].offset_object = bpy.data.objects[emptyname]
			bpy.context.object.modifiers["Array"].count = corners
			bpy.context.object.modifiers["Array"].use_merge_vertices = True
			bpy.context.object.modifiers["Array"].use_merge_vertices_cap = True
			bpy.context.object.modifiers["Array"].show_on_cage = True

			bpy.ops.object.select_all(action = "DESELECT")
			#bpy.context.scene.objects.active = o
			#o.select = True
			
			
			#context.scene.objects.active = empty
			#empty.select = True
			
			#bpy.ops.object.mode_set(mode = 'EDIT')
			
		else:
			print ("Vertex count must be 2")

	
	def execute(self, context):
		
		self.print_vert_details(context)
		
		return {'FINISHED'}
	
	def invoke(self, context, value):
		
		self.active_obj_name = context.scene.objects.active.name
		self.print_vert_details(context)
		
		return {'FINISHED'}
	
class RENDER_PT_publish(bpy.types.Panel):
	bl_idname = "scene.spiral"
	bl_label = "Spiral"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"


	def draw(self, context):
		
		layout = self.layout

		# initial options
		layout.label("Options", icon="FILE_SCRIPT")
		#layout.prop(p, "corners")

		layout.operator(Create.bl_idname, "Create spiral")


def register():
	bpy.utils.register_module(__name__)
	


def unregister():
	bpy.utils.unregister_module(__name__)
	


if __name__ == "__main__":
	try:
		unregister()
	except:
		pass
	register()


