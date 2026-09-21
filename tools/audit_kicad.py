"""Read-only structural KiCad audit. Does not replace KiCad ERC/DRC."""
import json,re
from pathlib import Path

def parse(text):
    tokens=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text)
    stack=[];root=None
    for t in tokens:
        if t=='(':
            n=[]
            if stack:stack[-1].append(n)
            stack.append(n)
        elif t==')':root=stack.pop()
        else:stack[-1].append(t.strip('"'))
    return root

def children(node,key):return [v for v in node if isinstance(v,list) and v and v[0]==key]

def run():
    r=Path(__file__).resolve().parents[1];board=parse((r/'hardware/original/dsss.kicad_pcb').read_text());sch=parse((r/'hardware/original/dsss.kicad_sch').read_text())
    fps=children(board,'footprint');pads=[p for f in fps for p in children(f,'pad')]
    connected=[p for p in pads if any(len(n)>1 and n[1]!='0' for n in children(p,'net'))]
    report=dict(board_footprints=len(fps),board_tracks=len(children(board,'segment')),board_vias=len(children(board,'via')),board_zones=len(children(board,'zone')),declared_nets=len(children(board,'net')),pads=len(pads),pads_with_nonzero_net=len(connected),schematic_wires=len(children(sch,'wire')),schematic_placed_symbols=len(children(sch,'symbol')),erc_run=False,drc_run=False,fabrication_ready=False,reason='No routed tracks and no schematic wires; user confirms conceptual placement study.')
    (r/'hardware/audit/structural-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':run()
