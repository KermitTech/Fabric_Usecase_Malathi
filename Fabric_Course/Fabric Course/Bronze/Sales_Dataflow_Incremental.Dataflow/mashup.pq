[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[IncrementalRefreshSettings = [FilterColumnName = "sale_date", WindowSize = 1, WindowUnit = "Year", BucketUnit = "Year", BookmarkColumnName = "sale_date", ConsiderOnlyConcludedPeriods = false, RequireIncrementalRefreshQueryToFold = true], BindToDefaultDestination = true]
shared #"demo sales" = let
  Source = MySQL.Database("database-1.c5awoeiuuje1.us-east-1.rds.amazonaws.com", "demo"),
  #"Navigation 1" = Source{[Schema = "demo", Item = "sales"]}[Data]
in
  #"Navigation 1";
shared DefaultDestination = Lakehouse.Contents(null){[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data]{[lakehouseId = "9c3d1e3c-2765-4802-a6d4-f06f058e36bd"]}[Data];
