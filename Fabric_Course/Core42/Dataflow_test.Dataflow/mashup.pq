[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared Account = let
  Source = Salesforce.Data("https://login.salesforce.com/", [ApiVersion = 48]),
  #"Navigation 1" = Source{[Name = "Account"]}[Data]
in
  #"Navigation 1";
