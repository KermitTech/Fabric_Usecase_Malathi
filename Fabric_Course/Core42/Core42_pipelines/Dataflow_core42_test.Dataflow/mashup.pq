[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[BindToDefaultDestination = true]
shared #"bronze Account" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "Account"]}[Data]
in
  #"Navigation 1";
[BindToDefaultDestination = true]
shared #"bronze Contact" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "Contact"]}[Data]
in
  #"Navigation 1";
[BindToDefaultDestination = true]
shared #"bronze Lead" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "Lead"]}[Data]
in
  #"Navigation 1";
[BindToDefaultDestination = true]
shared #"bronze Opportunity" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "Opportunity"]}[Data]
in
  #"Navigation 1";
[BindToDefaultDestination = true]
shared #"bronze Quote" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "Quote"]}[Data]
in
  #"Navigation 1";
[BindToDefaultDestination = true]
shared #"bronze User" = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "IMDBIDM_ZAA_Analytics_test"),
  #"Navigation 1" = Source{[Schema = "bronze", Item = "User"]}[Data]
in
  #"Navigation 1";
shared DefaultDestination = let
  Source = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  #"Navigation 1" = Source{[workspaceId = "c6ff84ef-9490-4ae1-b7c6-be106bd4cb8c"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "a996a5ec-3d06-46cf-a50b-45a77716c300"]}[Data]
in
  #"Navigation 2";
