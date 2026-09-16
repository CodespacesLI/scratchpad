# Dev Container fuer scratchpad: alles vorinstalliert, nichts auf dem eigenen Rechner.
# Enthalten: Node.js 22 + npm, Git, Python 3, Claude Code, Codex CLI und die
# Systempakete fuer Playwright-Browser (Schritt 7 der Uebung).
FROM mcr.microsoft.com/devcontainers/javascript-node:22-bookworm

# safe.directory: Der Projektordner ist vom Host eingebunden und gehoert dort einem
# anderen Nutzer; ohne diese Einstellung verweigert Git mit "dubious ownership".
RUN apt-get update \
 && export DEBIAN_FRONTEND=noninteractive \
 && apt-get install -y --no-install-recommends python3 python-is-python3 \
 && npx -y playwright install-deps chromium \
 && rm -rf /var/lib/apt/lists/* /root/.npm \
 && git config --system --add safe.directory '*'

RUN npm install -g @openai/codex && npm cache clean --force

USER node
RUN curl -fsSL https://claude.ai/install.sh | bash
ENV PATH=/home/node/.local/bin:$PATH

# Logins ueberleben einen Neubau des Containers: beide Ordner sind Volumes
# (devcontainer.json). CLAUDE_CONFIG_DIR legt auch .claude.json dort ab.
ENV CLAUDE_CONFIG_DIR=/home/node/.claude
RUN mkdir -p /home/node/.claude /home/node/.codex
