# Script version 1.0 
import adsk.core, adsk.fusion, traceback

def run(context):
    # Array for collecting messages to display at the end of the script.
    global script_summary  
    script_summary = []

    # list of functions 
    getPoints()             # Switches to designwork space to get points for later use.
    flipWCS()               # Flips the WCS 180 degrees. Will also flip it back to the default WCS.
    scriptSummary()         # Displays a summary at the end of the script.

def addMessage(msg):        # This function adds messages throughout the script to give a summary at the end.
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        script_summary.append(f"\u2022 {msg}\n")
    except:
        ui.messageBox(f"addMessage(): failed:\n{traceback.format_exc()}")

def in_cm(x):               # This function converts inches to cm.
    return x * 2.54

def getPoints():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.workspaces.itemById('FusionSolidEnvironment').activate() 
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent

        global melvinPoint, melvinFlippedPoint
        melvinPoint = rootComp.constructionPoints.itemByName('Melvin WCS')
        melvinFlippedPoint = rootComp.constructionPoints.itemByName('Melvin Flipped WCS')

        if not melvinPoint:
            # This is to catch panels made from an earlier script verion.
            melvinPoint = rootComp.constructionPoints.itemByName('Point2')

        if not melvinFlippedPoint:
            idOrigin()
            createOrigin()
    except:
        ui.messageBox(f"getPoints(): failed:\n{traceback.format_exc()}")

def idOrigin():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent
        # Find the edge of the stud body for our WCS
        studs = [body for body in rootComp.bRepBodies if body.name.startswith("Stud")]

        # Initialize min and max values
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        # Loop through all "Stud" bodies and expand bounds
        for body in studs:
            box = body.boundingBox
            min_x = min(min_x, box.minPoint.x)
            min_y = min(min_y, box.minPoint.y)
            min_z = min(min_z, box.minPoint.z)
            max_x = max(max_x, box.maxPoint.x)
            max_y = max(max_y, box.maxPoint.y)
            max_z = max(max_z, box.maxPoint.z)

        # Create Point3D objects for easy use later
        global stud_max_point, stud_min_point
        stud_max_point = adsk.core.Point3D.create(max_x, max_y, max_z) # This is used to identify a east return, which affect the origin position.
        stud_min_point = adsk.core.Point3D.create(min_x, min_y, min_z) # This is used to identify a west return. No affect to the origin.
        
        # Find the edge of the stud body for our WCS
        track = [body for body in rootComp.bRepBodies if body.name.startswith("Track")]

        # Initialize min and max values
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        # Loop through all "Stud" bodies and expand bounds
        for body in track:
            box = body.boundingBox
            min_x = min(min_x, box.minPoint.x)
            min_y = min(min_y, box.minPoint.y)
            min_z = min(min_z, box.minPoint.z)
            max_x = max(max_x, box.maxPoint.x)
            max_y = max(max_y, box.maxPoint.y)
            max_z = max(max_z, box.maxPoint.z)

        # Create Point3D objects for easy use later
        global track_min_point
        track_min_point = adsk.core.Point3D.create(min_x, min_y, min_z)
        
    except:
        ui.messageBox(f"{traceback.format_exc()}", "idOrigin(): failed!")

def createOrigin():
    app = adsk.core.Application.get()
    ui = app.userInterface
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent

    try:
        body = rootComp.bRepBodies.item(0)
        
        # Compute overall bounding box extents
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')

        for face in body.faces:
            boundingBox = face.boundingBox
            min_x = min(min_x, boundingBox.minPoint.x)
            max_x = max(max_x, boundingBox.maxPoint.x)
            min_y = min(min_y, boundingBox.minPoint.y)
            max_y = max(max_y, boundingBox.maxPoint.y)
            min_z = min(min_z, boundingBox.minPoint.z)
            max_z = max(max_z, boundingBox.maxPoint.z)
        
        # Back-bottom-left corner
        corner_x, corner_y, corner_z = min_x, max_y, min_z

       # Define WCS X axis position
        if any("Stud" in body.name for body in rootComp.bRepBodies):
            offset_x = stud_min_point.x
        else:
            offset_x = corner_x + in_cm(0.0625)

        # Define WCS Y axis position
        if any("Track" in body.name for body in rootComp.bRepBodies):
            offset_z = track_min_point.z
        else:
            offset_z = corner_z + in_cm(0.0625)

        # Define WCS Z axis position
        offset_y = corner_y - in_cm(6.0)

        # Create point
        construction_point = adsk.core.Point3D.create(offset_x, offset_y, offset_z)
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        sketchPoint = sketch.sketchPoints.add(construction_point)
        constructionPoints = rootComp.constructionPoints
        point_input = constructionPoints.createInput()
        point_input.setByPoint(sketchPoint)
        new_point = constructionPoints.add(point_input)
        new_point.name = 'Melvin Flipped WCS'
        app.activeViewport.fit()

        global melvinFlippedPoint
        melvinFlippedPoint = rootComp.constructionPoints.itemByName('Melvin Flipped WCS')
        addMessage("Melvin Flipped WCS was created.")
    except:
        ui.messageBox(f"flipOrgin(): failed:\n{traceback.format_exc()}")

def flipWCS():
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.workspaces.itemById('CAMEnvironment').activate()

    try:
        # Define global variables
        global cam, setups, doc, cam_product,camOcc, setupInput
    
        # Switch to Manufacture Workspace
        
        cam = adsk.cam.CAM.cast(app.activeProduct)
        setups = cam.setups

        # Find the setup named "Melvin"
        for setup in setups:
            if setup.name == "Melvin":
                setup = setup
                break

        origin_refs = setup.parameters.itemByName('wcs_origin_point').value.value
        origin_name = origin_refs[0].name
        #ui.messageBox(f"WCS Origin: {origin_name}")
                
        if origin_name != 'Melvin Flipped WCS':
            # Select origin for Melvin setup
            setup.parameters.itemByName('wcs_origin_point').value.value = [melvinFlippedPoint]
            setup.parameters.itemByName('wcs_orientation_flipX').value.value = False
            setup.parameters.itemByName('wcs_orientation_flipZ').value.value = True

            perimeter_op = None
            for op_index in range(setup.operations.count):
                op = setup.operations.item(op_index)
                if op.name.startswith("Perimeter"):
                    perimeter_op = op
                    break 
                else:
                    perimeter_op = setup.operations.item(0)

            perimeter_op.parameters.itemByName('entryPositions').value.value = [melvinFlippedPoint]
            addMessage("Melvin WCS is set to the bottom-left corner.")

        else:
            # Select origin for default Melvin WCS
            setup.parameters.itemByName('wcs_origin_point').value.value = [melvinPoint]
            setup.parameters.itemByName('wcs_orientation_flipX').value.value = True
            setup.parameters.itemByName('wcs_orientation_flipZ').value.value = True

            perimeter_op = None
            for op_index in range(setup.operations.count):
                op = setup.operations.item(op_index)
                if op.name.startswith("Perimeter"):
                    perimeter_op = op
                    break 
                else:
                    perimeter_op = setup.operations.item(0)

            perimeter_op.parameters.itemByName('entryPositions').value.value = [melvinPoint]
            addMessage("Melvin WCS is set to the top-right corner.")

        cam.generateToolpath(perimeter_op)
        addMessage("The Melvin setup is ready to post process!")

    except:
        ui.messageBox(f"copySetup(): failed:\n{traceback.format_exc()}")
    
def scriptSummary():
    app = adsk.core.Application.get()
    ui = app.userInterface
      
    try:
        if len(script_summary) == 0:
            addMessage("Everything looks great!")

        full_message = "\n".join(script_summary)
        ui.messageBox(full_message, "Script Summary", 
                    adsk.core.MessageBoxButtonTypes.OKButtonType,
                    adsk.core.MessageBoxIconTypes.InformationIconType)
    except:
        ui.messageBox(f"scriptSummary(): failed:\n{traceback.format_exc()}")
 