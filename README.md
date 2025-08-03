# Quickly find and edit the instanced collection source !

Lost in a large scene with lots of instances ? This addon adds one button "Show instance source" in the Object Properties > under "Instancing".

![panel](/presentation/presentation_panel.png)
![panel](/presentation/presentation_report.png)


### Overview
This addon looks for the source Collection through all the Scenes and View Layers, switched you to the right Scene and View Layer, selects the right Collection, the objects inside and frames them.


### Notes
- If a View Layer has the source Collection already "checked" it switched to that layer. 
- If none of the View Layers have that collection "checked", it checks it in the current View Layer.
- If the source Collection is nowhere to be found in the existing Scenes, it creates a new Scene with the Collection name and switched to it.