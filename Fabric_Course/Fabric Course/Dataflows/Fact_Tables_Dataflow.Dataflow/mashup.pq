[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Append"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[BindToDefaultDestination = true]
shared Fact_inventory = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "d5421d9d-313d-44a1-930c-dbfba5782a76"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Supply_Chain.Cleansed_inventory", ItemKind = "Table"]}[Data]
in
  #"Navigation 2";
shared DefaultDestination = Fabric.Warehouse([CreateNavigationProperties = false]){[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data]{[warehouseId = "5aed95e5-3a2c-497b-ac98-82c55dc7b36d"]}[Data];
[BindToDefaultDestination = true]
shared Fact_shipping = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "d5421d9d-313d-44a1-930c-dbfba5782a76"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Supply_Chain.Cleansed_shipping", ItemKind = "Table"]}[Data]
in
  #"Navigation 2";
[BindToDefaultDestination = true]
shared Fact_Demand_Predictions = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "d5421d9d-313d-44a1-930c-dbfba5782a76"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Supply_Chain.Demand_Predictions", ItemKind = "Table"]}[Data]
in
  #"Navigation 2";
