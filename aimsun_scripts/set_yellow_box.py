"""Sets yellow box for all nodes in Aimsun."""

oftype = model.getCatalog().getObjectsByType(model.getType("GKNode"))
for node in oftype.values():
    node.setYellowBox(True)
print("Done")
