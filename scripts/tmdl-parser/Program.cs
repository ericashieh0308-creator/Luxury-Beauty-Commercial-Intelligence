using Microsoft.AnalysisServices.Tabular;

if (args.Length != 1 || !Directory.Exists(args[0]))
{
    Console.Error.WriteLine("Provide the path to the semantic model's definition directory.");
    return 2;
}

try
{
    Database database = TmdlSerializer.DeserializeDatabaseFromFolder(Path.GetFullPath(args[0]));
    Model model = database.Model;
    var targets = new HashSet<string>();
    foreach (Table table in model.Tables)
    {
        foreach (Column column in table.Columns)
        {
            foreach (Variation variation in column.Variations)
            {
                if (variation.Relationship is not SingleColumnRelationship relationship ||
                    relationship.FromColumn != column ||
                    variation.DefaultHierarchy?.Table != relationship.ToColumn?.Table ||
                    relationship.ToColumn is null)
                {
                    throw new InvalidOperationException($"Invalid date variation on {table.Name}.{column.Name}.");
                }
                targets.Add(relationship.ToColumn.Table.Name);
            }
        }
    }
    foreach (Table table in model.Tables.Where(table => table.ShowAsVariationsOnly))
    {
        if (!targets.Contains(table.Name))
        {
            throw new InvalidOperationException($"{table.Name}: ShowAsVariationsOnly has no incoming variation.");
        }
    }
    Console.WriteLine(
        $"Microsoft TOM deserialized {model.Tables.Count} tables, " +
        $"{model.Tables.Sum(table => table.Measures.Count)} measures, " +
        $"and {model.Relationships.Count} relationships. Verified {targets.Count} variation target tables.");
    return 0;
}
catch (Exception error)
{
    Console.Error.WriteLine(error.ToString());
    return 1;
}
