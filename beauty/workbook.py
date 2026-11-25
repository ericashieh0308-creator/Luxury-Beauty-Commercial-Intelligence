"""Generate the linked illustrative financial model."""
import argparse
from pathlib import Path
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from .finance import Drivers, SCENARIOS, SEASONALITY
from .pipeline import BENCHMARK

SHEETS = ["ReadMe","Control_Panel","Assumptions","Industry_Benchmarks","Product_Economics",
          "Monthly_PnL","Budget_vs_Actual","Revenue_Forecast","Channel_Profitability","Promotion_ROI",
          "Price_Volume_Mix","Scenario_Analysis","Sensitivity_Analysis","Executive_Summary","Model_Checks"]
MONEY = '#,##0.00;[Red](#,##0.00);–'
PERCENT = '0.0%;[Red](0.0%);–'

def build(path):
    book = Workbook()
    book.remove(book.active)
    sheets = [book.create_sheet(f"{i:02}_{name}") for i,name in enumerate(SHEETS)]
    ref = lambda i, cell: f"'{sheets[i].title}'!{cell}"
    a = lambda row: ref(2,f"$B${row}")
    def put(i, headers, rows):
        sheet = sheets[i]
        sheet.append(headers)
        for row in rows:
            sheet.append(row)
    put(0,["Model guide","Use"],[
        ["Classification","Illustrative premium beauty retailer. All financial figures are simulated."],
        ["Currency","USD unless labeled CAD. CAD uses an illustrative user scenario rate."],
        ["Workflow","Select a scenario on 01, edit blue inputs on 02, then review 13 and 14."],
        ["Sign convention","Discounts, returns, COGS, and expenses appear as positive deductions."],
        ["Returns","Returns reverse discounted sales and restock at original unit cost."],
        ["Recalculation","Open in Excel and use Formulas > Calculate Now (F9)."],
        ["Budget vs. actual","Budget is Base. Simulated actual is the scenario selected on 01."],
        ["Source","All operating inputs are illustrative. Industry benchmarks are contextual only."]])
    put(1,["Editable control","Selected case"],[["Scenario","Base"]])
    dv = DataValidation(type="list",formula1='"Base,Bull,Bear"')
    sheets[1].add_data_validation(dv)
    dv.add(sheets[1]["B2"])
    d = Drivers()
    put(2,["Simulated assumption","Editable value","Unit"],[
        ("Price",d.price,"USD"),("Cost",d.cost,"USD"),("Units",d.units,"units"),
        ("Discount",d.discount,"%"),("Returns",d.returns,"%"),("Online",d.online,"%"),
        ("Fulfillment",d.fulfillment,"USD"),("Fees",d.fees,"%"),("Other variable",d.other_variable,"%"),
        ("Fixed",d.fixed,"USD"),("Marketing",d.marketing,"USD"),("Return handling",d.return_handling,"USD"),
        ("Premium mix",.30,"%"),("Promotion discount",.15,"%"),("Volume uplift",.20,"%"),
        ("Campaign cost",1500,"USD"),("CAD per USD (hypothetical)",1.35,"CAD/USD")])
    put(3,BENCHMARK,[])
    put(4,["Illustrative SKU","Mix","List USD","Unit COGS USD","Net price per ordered unit",
           "Unit gross profit","Gross margin","Gross profit at +10% cost","List CAD",
           "Simulated monthly net revenue","Simulated monthly GP","GP contribution"],[
        ["Core",f"=1-{a(14)}",f"={a(2)}*0.90",f"={a(3)}*0.91",
         f"=C2*(1-{a(5)})*(1-{a(6)})",f"=E2-D2*(1-{a(6)})",'=IF(E2=0,"",F2/E2)',
         f"=E2-D2*1.1*(1-{a(6)})",f"=C2*{a(18)}",f"=B2*{a(4)}*E2",f"=B2*{a(4)}*F2",'=IF(SUM(K$2:K$3)=0,"",K2/SUM(K$2:K$3))'],
        ["Premium",f"={a(14)}",f"={a(2)}*1.23",f"={a(3)}*1.21",
         f"=C3*(1-{a(5)})*(1-{a(6)})",f"=E3-D3*(1-{a(6)})",'=IF(E3=0,"",F3/E3)',
         f"=E3-D3*1.1*(1-{a(6)})",f"=C3*{a(18)}",f"=B3*{a(4)}*E3",f"=B3*{a(4)}*F3",'=IF(SUM(K$2:K$3)=0,"",K3/SUM(K$2:K$3))']])
    put(11,["Simulated case","Growth","Cost inflation","Discount delta","Annual revenue","Annual operating profit"],
        [(name,*drivers,f'=SUMIF({ref(7,"$A$2:$A$37")},A{r},{ref(7,"$L$2:$L$37")})',
          f'=SUMIF({ref(7,"$A$2:$A$37")},A{r},{ref(7,"$R$2:$R$37")})')
         for r,(name,drivers) in enumerate(SCENARIOS.items(),2)])
    forecast_rows = []
    for scenario_row, name in enumerate(SCENARIOS, 2):
        for month, index in enumerate(SEASONALITY,1):
            r = len(forecast_rows)+2
            forecast_rows.append([f"={ref(11,f'A{scenario_row}')}",month,index,
                f"={a(4)}*(1+{ref(11,f'B{scenario_row}')})*C{r}",
                f"=SUMPRODUCT({ref(4,'B2:B3')},{ref(4,'C2:C3')})",
                f"=SUMPRODUCT({ref(4,'B2:B3')},{ref(4,'D2:D3')})*(1+{ref(11,f'C{scenario_row}')})",
                f"=MIN(1,MAX(0,{a(5)}+{ref(11,f'D{scenario_row}')}))",f"={a(6)}",
                f"=D{r}*E{r}",f"=I{r}*G{r}",f"=(I{r}-J{r})*H{r}",f"=I{r}-J{r}-K{r}",
                f"=D{r}*(1-H{r})*F{r}",f"=L{r}-M{r}",
                f"=D{r}*({a(7)}*{a(8)}+H{r}*{a(13)})+L{r}*({a(9)}+{a(10)})+{a(12)}",
                f"=N{r}-O{r}",f"={a(11)}",f"=P{r}-Q{r}"])
    put(7,["Case","Month","Seasonality","Units","Weighted list USD","Weighted unit cost USD","Discount %",
           "Returns %","Gross sales","Discounts","Returns","Net revenue","COGS","Gross profit","Variable expense",
           "Contribution","Fixed expense","Operating profit"],forecast_rows)
    put(5,["Period","Gross sales","Discounts","Returns","Net revenue","COGS","Gross profit","Gross margin",
           "Variable expense","Contribution","Fixed expense","Operating profit","Operating margin"],[
        [month,*[f'=SUMIFS({ref(7, f"${c}$2:${c}$37")},{ref(7,"$A$2:$A$37")},{ref(1,"$B$2")},{ref(7,"$B$2:$B$37")},A{r})'
        for c in "IJKLMN"],f'=IF(E{r}=0,"",G{r}/E{r})',*[f'=SUMIFS({ref(7,f"${c}$2:${c}$37")},{ref(7,"$A$2:$A$37")},{ref(1,"$B$2")},{ref(7,"$B$2:$B$37")},A{r})'
        for c in "OPQR"],f'=IF(E{r}=0,"",L{r}/E{r})'] for r,month in enumerate(range(1,13),2)] +
        [["Annual",*[f"=SUM({c}2:{c}13)" for c in "BCDEFG"],'=IF(E14=0,"",G14/E14)',
          *[f"=SUM({c}2:{c}13)" for c in "IJKL"],'=IF(E14=0,"",L14/E14)']])
    variance_rows = []
    for month in range(1,13):
        for label, fc, pl, sign in [("Revenue","L","E",1),("Gross profit","N","G",1),("Variable expense","O","I",-1),
                                    ("Fixed expense","Q","K",-1),("Operating profit","R","L",1)]:
            r = len(variance_rows)+2
            variance_rows.append([month,label,f"={ref(7,fc+str(month+1))}",f"={ref(5,pl+str(month+1))}",
                f"=D{r}-C{r}",f'=IF(C{r}=0,"",E{r}/ABS(C{r}))',
                f'=IF(E{r}=0,"On plan",IF(E{r}*{sign}>0,"Favorable","Unfavorable"))',
                f'=SUMIF(B$2:B{r},B{r},E$2:E{r})'])
    put(6,["Month","Metric","Budget","Simulated actual","Variance","Variance %","Direction","YTD variance"],variance_rows)
    monthly = lambda col: ref(5,col+"14")
    put(8,["Channel (simulated annual)","Share","Revenue","Gross profit","Fulfillment","Payment fees",
           "Marketing","Return handling","Other variable","Contribution","Contribution margin"],[
        [name, share, f"={monthly('E')}*B{r}",f"={monthly('G')}*B{r}",
         f"={units}*B{r}*{a(8)}" if name=="E-commerce" else "=0",
         f"=C{r}*{a(9)}",f"={a(12)}*12*B{r}",f"={units}*B{r}*{a(6)}*{a(13)}",
         f"=C{r}*{a(10)}",f"=D{r}-SUM(E{r}:I{r})",f'=IF(C{r}=0,"",J{r}/C{r})']
        for r,name,share,units in [
            (2,"Store",f"=1-{a(7)}",f'SUMIF({ref(7,"A2:A37")},{ref(1,"B2")},{ref(7,"D2:D37")})'),
            (3,"E-commerce",f"={a(7)}",f'SUMIF({ref(7,"A2:A37")},{ref(1,"B2")},{ref(7,"D2:D37")})')]])
    unit_cost = f"({a(3)}*(1-{a(6)})+{a(7)}*{a(8)}+{a(6)}*{a(13)})"
    keep = f"(1-{a(9)}-{a(10)})"
    def unit_contribution(discount):
        return f"({a(2)}*(1-{discount})*(1-{a(6)})*{keep}-{unit_cost})"
    put(9,["Simulated promotion metric","Baseline","Promotion"],[
        ["Units",f"={a(4)}",f"=B2*(1+{a(16)})"],
        ["Net revenue",f"=B2*{a(2)}*(1-{a(5)})*(1-{a(6)})",f"=C2*{a(2)}*(1-{a(15)})*(1-{a(6)})"],
        ["Gross profit",f"=B3-B2*{a(3)}*(1-{a(6)})",f"=C3-C2*{a(3)}*(1-{a(6)})"],
        ["Contribution",f"=B2*{unit_contribution(a(5))}-{a(12)}",f"=C2*{unit_contribution(a(15))}-{a(12)}-{a(17)}"],
        ["Incremental contribution net of campaign",None,"=C5-B5"],
        ["ROI",None,f'=IF({a(17)}=0,"",C6/{a(17)})'],
        ["Breakeven units",None,f'=IF({unit_contribution(a(15))}<=0,"",MAX(0,(B5+{a(12)}+{a(17)})/{unit_contribution(a(15))}))'],
        ["Required uplift",None,'=IF(OR(C8="",B2=0),"",C8/B2-1)'],
        ["Margin dilution",None,'=IF(OR(B3=0,C3=0),"",C4/C3-B4/B3)'],
        ["Incremental units",None,"=C2-B2"],["Incremental revenue",None,"=C3-B3"],
        ["Incremental gross profit",None,"=C4-B4"],["Campaign cost",None,f"={a(17)}"],
        ["Breakeven discount",None,f'=IFERROR(IF(AND(ISNUMBER(C16),C16>=0,C16<=1),C16,""),"")'],
        ["Unbounded discount solution",None,
         f'=IF(C2*{a(2)}*(1-{a(6)})*{keep}<=0,"",(C2*{unit_contribution("0")}-{a(12)}-{a(17)}-B5)/(C2*{a(2)}*(1-{a(6)})*{keep}))']])
    sheets[9].row_dimensions[16].hidden = True
    put(10,["Illustrative shared SKU","Budget units","Actual units","Budget net USD","Actual net USD",
            "Price","Volume","Mix"],[
        [f"={ref(4,f'A{r}')}",f"=SUM({ref(7,'D2:D13')})*{ref(4,f'B{r}')}",
         f'=SUMIF({ref(7,"A2:A37")},{ref(1,"B2")},{ref(7,"D2:D37")})*{ref(4,f"B{r}")}',
         f"={ref(4,f'E{r}')}",
         f'= {ref(4,f"C{r}")}*(1-MIN(1,MAX(0,{a(5)}+SUMIF({ref(11,"A2:A4")},{ref(1,"B2")},{ref(11,"D2:D4")}))))*(1-{a(6)})',
         f"=C{r}*(E{r}-D{r})",f"=IF(SUM(B$2:B$3)=0,0,(SUM(C$2:C$3)-SUM(B$2:B$3))*B{r}/SUM(B$2:B$3)*D{r})",
         f"=(C{r}-B{r})*D{r}-G{r}"] for r in (2,3)] +
         [["Bridge total",None,None,None,None,"=SUM(F2:F3)","=SUM(G2:G3)","=SUM(H2:H3)"]])
    put(12,["Discount / volume uplift",0,.1,.2,.3,.4],[
        [disc,*[f"={a(4)}*(1+{c}$1)*{unit_contribution(f'$A{r}')}-{a(4)}*{unit_contribution(a(5))}-{a(17)}"
                for c in "BCDEF"]] for r,disc in enumerate([0,.05,.1,.15,.2,.25,.3],2)])
    put(13,["Management summary","Simulated value"],[
        ["Annual net revenue",f"={monthly('E')}"],["Annual operating profit",f"={monthly('L')}"],
        ["Gross margin",f"={monthly('H')}"],["Promotion ROI",f"={ref(9,'C7')}"],
        ["Operating variance vs Base",f"=B3-{ref(11,'F2')}"],
        ["Decision",f'=IF(B6<0,"Review unit volume, discounts and unit cost before expanding spend.","Verify assumptions before scaling spend.")']])
    put(14,["Reconciliation (target zero)","Residual","Status"],[
        ["Net revenue",f"={monthly('B')}-{monthly('C')}-{monthly('D')}-{monthly('E')}"],
        ["Operating profit",f"={monthly('G')}-{monthly('I')}-{monthly('K')}-{monthly('L')}"],
        ["Channel contribution",f"=SUM({ref(8,'J2:J3')})-{monthly('J')}"],
        ["PVM vs forecast",f"=SUM({ref(10,'F4:H4')})-({monthly('E')}-{ref(11,'E2')})"],
        ["Operating variance bridge",f"={ref(6,'H58')}-{ref(6,'H59')}-{ref(6,'H60')}-{ref(6,'H61')}"],
    ])
    for r in range(2,7):
        sheets[14][f"C{r}"] = f'=IF(ABS(B{r})<0.000001,"PASS","CHECK")'
    chart = BarChart()
    chart.title = "Illustrative annual operating profit (USD)"
    chart.add_data(Reference(sheets[11],min_col=6,min_row=1,max_row=4),titles_from_data=True)
    chart.set_categories(Reference(sheets[11],min_col=1,min_row=2,max_row=4))
    sheets[13].add_chart(chart,"D2")
    for index,sheet in enumerate(sheets):
        sheet.freeze_panes = "B2"
        sheet.sheet_view.showGridLines = False
        for column in sheet.columns:
            letter = get_column_letter(column[0].column)
            lengths = [len(str(cell.value or "")) for cell in column if cell.data_type != "f"]
            sheet.column_dimensions[letter].width = min(72,max(19,max(lengths,default=0)+3))
            for cell in column:
                if cell.row == 1:
                    cell.fill = PatternFill("solid",fgColor="211C1A")
                    cell.font = Font(color="FFFFFF",bold=True)
                elif cell.data_type in {"n","f"}:
                    cell.number_format = MONEY
                if (index in {1,2} and cell.column==2 and cell.row>1) or (index==11 and cell.column in {2,3,4} and cell.row>1):
                    cell.fill = PatternFill("solid",fgColor="DFEBF8")
                    cell.font = Font(color="144C76")
        for cell in sheet[1]:
            cell.alignment = Alignment(wrap_text=True,vertical="center")
        sheet.row_dimensions[1].height = 32
    for index,columns in {4:"BGL",5:"HM",6:"F",7:"GH",8:"BK",11:"BCD"}.items():
        for c in columns:
            for cell in sheets[index][c][1:]:
                cell.number_format = PERCENT
    for r in (5,6,7,9,10,14,15,16):
        sheets[2][f"B{r}"].number_format = PERCENT
    for pos in ("C7","C9","C10","C15","C16"):
        sheets[9][pos].number_format = PERCENT
    for pos in ("B4","B5"):
        sheets[13][pos].number_format = PERCENT
    for cell in sheets[12][1][1:]+tuple(sheets[12]["A"][1:]):
        cell.number_format = PERCENT
    path.parent.mkdir(parents=True,exist_ok=True)
    book.save(path)

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output",type=Path,default=Path("models/excel/Luxury_Beauty_Commercial_Financial_Model.xlsx"))
    build(cli.parse_args().output)
