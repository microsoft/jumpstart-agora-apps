
pushd %~dp0

if not exist .env\ (
  python -m venv .env
)
call .env\Scripts\activate

python -m pip install "eclipse_opcua @ git+https://%AZURE_DEVOPS_GIT_PAT%@dev.azure.com/ISE-Industrial-Engineering/Industrial%%20Metaverse%%20-%%20Software%%20Delivery/_git/Industrial%%20Metaverse%%20-%%20Software%%20Delivery@darienp/opc-plc-kepware#subdirectory=src/opcua-plc-server"

plc_server.exe fluid-demo-real.json

popd
