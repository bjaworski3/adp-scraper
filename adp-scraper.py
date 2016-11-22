import requests
import pprint
import json
import getpass

pp = pprint.PrettyPrinter(indent=4)

header = {
    'User-Agent': 'Mozilla/5.0',
    "Host": "agateway.adp.com",
    "Connection": "keep-alive",
    "Origin": "https://my.adp.com"
}

payload = {
    'target': 'https://my.adp.com/static/redbox',
    'user': raw_input("Enter username: "),
    'password': getpass.getpass()
}
headers = {'User-Agent': 'Mozilla/5.0'}

key_list = [
    'grossPayAmount',
    'deductions',
    'netPayAmount'
]

full_statements = dict()
parsed_statements = dict()

with requests.Session() as s:
    r = s.get('https://my.adp.com/static/redbox/login.html')
    #print r.text

    p = s.post("https://agateway.adp.com/siteminderagent/forms/login.fcc", data=payload)
    # print the html returned or something more intelligent to see if it's a successful login page.
    #print p.text

    # An authorised request.
    r = s.get("https://my.adp.com/v1_0/O/A/payStatements?adjustments=yes&numberoflastpaydates=100")
    json_statements = json.loads(r.text)

    for statement in json_statements['payStatements']:
        if not statement['payAdjustmentIndicator']:
            r2 = s.get("https://my.adp.com%s" % statement['payDetailUri']['href'])
            json_detail_statement = json.loads(r2.text)
            # print json_detail_statement['payStatement'].keys()
            pay_date = json_detail_statement['payStatement']['payDate']
            full_statements[pay_date] = json_detail_statement['payStatement']

# pp.pprint(full_statements)

for date in full_statements.keys():
    parsed_statements[date] = dict()
    parsed_statements[date]['grossPayAmount'] = full_statements[date]['grossPayAmount']['amountValue']
    parsed_statements[date]['netPayAmount'] = full_statements[date]['netPayAmount']['amountValue']
    for deduction in full_statements[date]["deductions"]:
        name = deduction['CodeName'].rstrip().encode('utf-8')
        try:
            if abs(deduction['deductionAmount']['amountValue']) != parsed_statements[date]['netPayAmount']:
                parsed_statements[date][name] = deduction['deductionAmount']['amountValue']
        except KeyError:
            # No deduction was done this pay check
            pass

pp.pprint(parsed_statements)
