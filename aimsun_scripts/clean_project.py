"""Removes objects in Aimsun."""

for GKtypeRemove in [
        "GKCenConnectionNewCmd",
        "GKCentroid",
        "GKCentroidConfiguration",
        "GKControlPlan",
        "GKDetector",
        "GKExperiment",
        "GKGenericExperiment",
        "GKGenericScenario",
        "GKMasterControlPlan",
        "GKMetering",
        "GKODMatrix",
        "GKPathAssignment",
        "GKPolicy",
        "GKRealDataSet",
        "GKReplication",
        "GKScenario",
        "GKStrategy",
        "GKTrafficDemand",
        "GKTurningClosingChange"
]:
    oftype = model.getCatalog().getObjectsByType(model.getType(GKtypeRemove))
    if oftype is not None:
        for object_remove in oftype.values():
            cmd = object_remove.getDelCmd()
            model.getCommander().addCommand(cmd)

deadObjects = model.getCatalog().clearDeathObjects()
# From Aimsun documentation: help/content/Aimsun Next Scripting/Examples/Object
# Creation and Use:
# Since the GKObjectDelCmd class is derived from GKCommand, it provides undo
# functionality. Therefore, to make the deletion permanent (non-undoable), add a
# null command:
model.getCommander().addCommand(None)
print("Done")
