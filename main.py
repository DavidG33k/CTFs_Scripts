from typing import Optional
import typer

from path_thraversal import AutomizedPathTraversal
from business_logic_vulnerabilities import infiniteMoneyCTF

app = typer.Typer()


@app.command()
def path_traversal_resolver(ctf_session_code: str):
    """
    An automized script to solve all path traversal CTFs of PortSwigger. 
    """
    AutomizedPathTraversal.main(ctf_session_code=ctf_session_code)

@app.command()
def infinite_money_ctf_resolver(ctf_session_code: str, session_cookie:str):
    """
    An automized script to solve the challange 'Infinite money logic flow'.
    """
    infiniteMoneyCTF.main(ctf_session_code=ctf_session_code, session_cookie=session_cookie)



if __name__ == "__main__":
    app()
