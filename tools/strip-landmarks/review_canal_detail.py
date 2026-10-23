"""Close views of the actual exported geometry plus surrounding city/interiors."""
exec(open('tools/strip-landmarks/review_venetian_water.py').read().split("for name in ['canal-bridge-clearance'")[0])
shots={'gondola-detail':([191,7,-735],[199,1,-726]),'pavilion-alignment':([166,24,-746],[188,2,-718]),'venetian-street':([90,5,-592],[140,7,-580])}
import sys
for name,(eye,target) in shots.items():
 if '--gondola-only' in sys.argv and name!='gondola-detail':continue
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;s.render.filepath=str((OUT/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
