# Zoe's Deck Theme

A CSS Loader theme that makes the Steam Deck feel as clean as an Apple product: Instrument Serif accent
titles, Oxygen everywhere else, rounded corners, liquid-glass UI and a calmer homescreen.

- **Claude:** start with [`CLAUDE.md`](CLAUDE.md), then [`docs/RESEARCH.md`](docs/RESEARCH.md).
- **Status:** research done, theme not built yet.

## Working from a Mac over SSH

The theme has to be built and tested *on the Deck* while it's in Gaming Mode, so the Mac is only a
keyboard and screen. Claude Code runs on the Deck.

### One-time setup on the Deck (Desktop Mode → Konsole)

The VS Code on the Deck is a sandboxed Flatpak, so run these in **Konsole**, not the VS Code terminal.

```sh
passwd                                   # set a password for "deck" if you never have
sudo systemctl enable --now sshd         # turn on SSH (survives reboots)
curl -fsSL https://claude.ai/install.sh | bash   # installs the `claude` command to ~/.local/bin
```

Then in **Settings → Display** set sleep to a long delay or never while plugged in (a sleeping Deck drops
the SSH connection), and switch to **Gaming Mode**.

### Every session, on the Mac

```sh
ssh deck@steamdeck.local                 # or deck@<Deck IP> (Settings → Internet → your network)
cd ~/Documents/"Zoe's Deck Theme"
claude
```

First message: **"Read CLAUDE.md and continue with the next steps."**

The first `claude` run prints a login link; open it on the Mac. Tip: `ssh-copy-id deck@steamdeck.local` once
from the Mac so you don't have to type the password every time.

**Prefer a GUI?** Install VS Code's **Remote - SSH** extension on the Mac, connect to
`deck@steamdeck.local`, open `~/Documents/Zoe's Deck Theme`, and install the Claude Code extension on the
remote side when prompted. It works the same as working on the Deck directly.

**To inspect the UI yourself** from Chrome on the Mac: `ssh -L 8080:127.0.0.1:8080 deck@steamdeck.local`,
then go to `chrome://inspect` → Configure → add `localhost:8080`.

## Layout

```
CLAUDE.md          handoff + rules for Claude
docs/RESEARCH.md   findings: CSS Loader format, class names, fonts, glass, homescreen plan
tools/cef.py       inspect or screenshot the live Steam UI (run on the Deck)
theme/             the theme itself (coming next), symlinked into ~/homebrew/themes/ZoesDeckTheme
```
