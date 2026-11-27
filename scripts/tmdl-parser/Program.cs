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
    Console.WriteLine(
        $"Microsoft TOM deserialized {model.Tables.Count} tables, " +
        $"{model.Tables.Sum(table => table.Measures.Count)} measures, " +
        $"and {model.Relationships.Count} relationships.");
    return 0;
}
catch (Exception error)
{
    Console.Error.WriteLine(error.ToString());
    return 1;
}
