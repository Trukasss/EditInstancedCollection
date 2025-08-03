# Quickly find and edit the instanced collection source !

Lost in a large scene with lots of instances ? This addon adds one button "Show instance source" in the Object Properties > under "Instancing".

![panel](/presentation/presentation_panel.png)
![panel](/presentation/presentation_report.png)


### Overview
This addon looks for the source collection through all the scenes and view layers, switched you to the right scene and view layer, selects the collection, the objects inside and frames them.


### Notes
- If a View Layer has the source collection already "checked" it switched to that layer. 
- If none of the View Layers have that collection "checked", is checks it in the current View Layer.
- If the source collection is nowhere to be found in the existing scenes, it creates a new scene with the collection name and switched to it.