# insilico_wgs

You can use this to create bedfiles from a refseq-database or you can do a coverage analysis using mpileup on a collection of validation samples from the novaseq and receive a bunch of output files with various coverage stats. 

# create bedfile

./create_bed.py

(copy pasted from excelsheet, sorry for the mess) 

Vi kan antingen få panelen beskriven till oss som en lista av gener eller en lista av specfika transkript
Folk på KG tenderar att skicka transkript och är inte så jäkla intresserade av intron-regioner. Får ni transcript så är det bara att skapa en liten textfil med varje transkript per rad, som här t ex i repot:
/insilico_panels/KG/[ny cool panel]/[nytt coolt panelnamn].txt

./create_bed.py -r refseq_20190301_ncbiRefSeq -t transcriptlistan -o outputmapp
OBS: Om man anger transkript namn så får man bara de exoniska regionerna + UTR-regioner för transkriptet. Och KG brukar vilja vara säker på att även splicesites är täckta ordentligt, vilket innebär att man behöver utöka regionerna med 2 baser. Gör då såhär bara:
./create_bed.py -r refseq_20190301_ncbiRefSeq -t transcriptlistan -o outputmapp -e 2

Ibland har dom inga specifika transkripts in mind utan man får en genlista, men ibland vill dom samtidigt ändå inte ha täckningsanalys på intronen, eller så vill dom ha ut täckningsinformation på specifika exon (och i båda fallen kan det bli lite bökigt att göra detta baserat på enbart gennamn -- hur numrerar man exonen? ibland har olika transkript i samma gen överlappande exon med olika längder, etc, TLDR: Det är drygt). Lösningen: Plocka ut längsta transkriptet för alla gener
./create_bed.py -r refseq_20190301_ncbiRefSeq -g genlista -o outputmapp -l yes -e 2

Är det bara genlista så som KK-folk brukar vilja (citat Emma Samuelsson "Vi vill ha det som vi brukar, rubbet! Tack!") så använder vi inte -l flaggan utan kör bara:
./create_bed.py -r refseq_20190301_ncbiRefSeq -g genlista -o outputmapp

OBS igen: Om transkript eller gener inte finns :O
Ibland finns inte genen/transkriptet i "databasen" som filen antyder är en nerladdning av refseqGenes från datum 20190301. I transkriptens fall kan det vara så att transkriptet uppdaterats sen nerladdningen (ovanligt), eller i genernas fall att dom har insett att det tidigare namnet var lite töntigt och ville ha ett coolare namn. 
Iallafall så ploppar dessa ut i en separat fil i outputmappen som heter något med "notfound.txt"
Vad gör man då?! 
Ja, greppa i refseq_20190301_ncbiRefSeq efter transkriptet/genen för att lugna sinnet kanske att inte skriptet bara är dum-i-huvet, men det har den faktiskt inte varit än så länge. 
Är det transkript som saknas skulle jag testa att ta bort versions-namnet i transkriptet, det efter "." alltså. Och kolla om det finns en äldre version eller nyare. Finns det en annan version skulle jag maila och fråga den som bad om panelen ifall det är ok att vi tar den existerande versionen istället, brukar vara OK.
Är det gener som saknas skulle jag gå in här:
https://www.genecards.org
Och söka efter det angivna gennamnet som inte hittas, och där kolla i listor efter synonymer/deprecated namn och försöka reda ut ifall det namnet vi har är det nyare coola namnet eller om vi sitter på det gamla töntiga namnet. Står det angivna gennamnet som dom skickade högst upp på sidan så är det tyvärr vi som har det töntiga namnet. Då får vi greppa efter synonymerna i vår fil tills att vi får en vettig träff.
Sen samlar man på sig modet...och lovar sig själv att ta en lång renande dusch i någon snar framtid och kör:
./replace_names.sh gammalt_namn nytt_namn
Det här har gjorts några gånger redan, kolla här i repot:
/create_bedfile/changes_made
Men om man är rädd att man förstört något så finns en backup i samma mapp. 

Historiskt sett, och inte egentligen på ett superorganiserat sätt så har jag haft min outputmapp för att skapa insilico-filer här:
/medstore/Development/WGS_validation/in_silico_panels/

Men nu tänker jag att vi ska spara bedfilerna i det här repot, eftersom filerna ändå är ganska små och det möjliggör versionshantering! FANTASTISKT JU. 

För att vara lite bättre organiserad har jag sparat alla genlistor/transkriptlistor som har skickats i detta googlesheet. "InSilicopaneler KK" & "InSilicopaneler KG".

# coverage analysis (for in silico panel verification into WGS analysis) 

you need to be root to run

cd to validate_wrapper subdirectory

./validate_wrapper /path/to/bedfile.bed [departmentID = KG/KK,PAT] [annotationlevel = 1/2/3/4/5]

results are saved here:
/medstore/Development/WGS_validation/in_silico_panels/${department}/validate/panels/

Now you need to extract various stats and add to an excelfile to be sent to responsible clinician for the insilico coverage verification (its a bit silly, it always works, and we should probably take up the fight on this at some point to save time for ourselves)

A template excelfile exits in boxsync:
/Dokument/WGS/konstitutionell/insilico

Sheet1: 
Paste results from /general_stats/panelname.bed_stats.tsv

Sheet 2 and 3:
Paste from /anybelow/panelname.bed_10x.csv
Paste from /anybelow/panelname.bed_20x.csv

SOME ADVICE: copy the results to /seqstore/webfolders/admin/insilico_results/ and navigate in the webbrowser to download the results
Then copy pate directly from there to column 1 in the excel sheet and in excel click on "Data" menu and choose "Text to columns" using "," as delimeter. 

Finally give the name some cool name, the name of the insilicopanel is a very cool name and also makes sense and then sent to the clinician! They will do amazing things with it. 

# place in silico panel into routine analysis

Give the bedfile an appropriate name and place it in the insilico-drectory of the department. Example here:
/medstore/results/wgs/KG/insilico_panels (for klinisk genetik)

Then update the json configfile with the new path, which is HERE at the moment, but this will probably change with the new WOPR version:
/apps/bio/dev_repos/WOPR/insilico_config.json 

Level is a bit confusing parameter, it is basically a code for the name-structure in the bedfile. Whether or not it contains gene, transcripts or exons, and in different combinations. 2 levels are in use in routine.
1 = GeneOnly 
2 = Gene_Transcript_Exon







