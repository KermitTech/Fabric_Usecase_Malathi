[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Account_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Account = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "Account"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Contact_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Contact = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "Contact"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Lead_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Lead = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "Lead"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Opportunity_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Opportunity = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "Opportunity"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Partner_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Partner = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "Partner"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "SBQQ__Quote__c_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared SBQQ__Quote__c = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "SBQQ__Quote__c"]}[Data]
in
  #"Navigation 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "User_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared User = let
  Source = Sql.Database("S5gzoyvwcpeubblw6gvssbnwz4-rtdqlr34a75u7e37nmobdnt7nm.datawarehouse.fabric.microsoft.com", "bronze"),
  #"Navigation 1" = Source{[Schema = "dbo", Item = "User"]}[Data]
in
  #"Navigation 1";
shared Opportunity_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "Opportunity_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Account_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "Account_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Contact_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "Contact_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Lead_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "Lead_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Partner_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "Partner", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared SBQQ__Quote__c_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "SBQQ__Quote__c_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared User_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "0954d773-1b76-4837-90bb-56305401112a"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "6ab9a74f-efc2-4c55-98ec-a6eb17866f8c"]}[Data],
  TableNavigation = Navigation_2{[Id = "User_new", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
