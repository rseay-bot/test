# Test the new stores from a computer with internet

Why: the cloud session cannot open store sites, so the stores added to the sweep tool (R59, R59b, R59c)
have never been tested, and some candidates have no known platform.

## 1. Load the tool (once)
Have Claude load the "mtgsweep CLI" artifact (https://claude.ai/artifact/LkJVcAgVbr3gM47tRgc6wd) to disk, or
download its files, then:

    cd mtgsweep
    python3 -m mtgsweep preflight          # should print PREFLIGHT OK
    python3 tests/test_matchers.py

## 2. Put these files in the tool folder
- tools/test_new_hosts.py   (copy of tools/test_candidates2.py without the "already known" skip)
- cand_added.json           the 111 stores already added to the lists (untested)
- cand_pending.json         ~70 stores NOT added: unknown platform, or held back (US location unconfirmed,
                            possible TCGplayer Pro storefront)

## 3. Test them (any machine with internet; Python 3 with requests installed)
    nohup python3 tools/test_new_hosts.py cand_added.json sealed added_out.jsonl 1500 > added.log 2>&1 &
    nohup python3 tools/test_new_hosts.py cand_pending.json sealed pending_out.jsonl 1500 > pending.log 2>&1 &

Each output line is JSON with: status (ok = the adapter read the store), rows, tgt_in_stock, country, currency.
Resumable: rerun the same command and it skips hosts already in the output file.
Stores that stay unreachable (neterr, hung) may need tools/tc_cffi.py (Chrome TLS) or a browser look.

## 4. Read the results
- added_out.jsonl: status ok with rows > 0 = keep. status ok with rows 0 = store has no sealed MTG now (keep, low value).
  Anything else = check by hand and remove from data/hosts/<platform>.txt if the store is dead or not US.
- pending_out.jsonl: add a host to the right data/hosts/<platform>.txt only if status is ok, rows > 0, country US.
  Then update EXPECTED in mtgsweep/hosts.py and rerun preflight.

## 5. Optional full run (checks everything, about 25 minutes in the cloud, longer at home)
    nohup python3 -m mtgsweep run --profile sealed --out runs/r60-sealed > runs/r60.log 2>&1 &
