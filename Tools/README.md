# JMF Tools R1.2.1

Command line tools for interacting with PRISMAsync via JMF/JDF.

Each tool accepts `-h` or `--help` for a full list of options.

> **Note:** Before using tools that communicate with PRISMAsync, enable JMF support in the PRISMAsync Settings Editor. The default JMF port is **8010**.

---

## SetupConfig

Creates the `.config` folder in the tools directory and populates it with default files used by the other tools: `SubmitQueueEntry.jmf`, `QueueStatus.jmf`, `RemoveQueueEntry.jmf`, `Template.jdf`, and `Test.pdf`.

Run this once after installation before using the other tools.

```
SetupConfig.exe [--verify]
```

| Argument | Short | Description |
|---|---|---|
| `--verify` | | Only check that required `.config` files exist; do not create or modify anything |

---

## CreateTestPDF

Creates a simple test PDF file for use with the other tools.

```
CreateTestPDF.exe [--output FILE] [--pages N] [--title TEXT] [--content TEXT] [--pagesize SIZE] [--config] [--blackwhite] [--list-sizes]
```

| Argument | Short | Description |
|---|---|---|
| `--output FILE` | `-o` | Output file path (default: `Test.pdf`) |
| `--pages N` | `-p` | Number of pages (default: `1`) |
| `--title TEXT` | `-t` | Title/header text on each page (default: `Test PDF`) |
| `--content TEXT` | `-c` | Content on each page; use `##` to insert the page number |
| `--pagesize SIZE` | `-ps` | Page size (default: `a4`). Use `--list-sizes` to see all options |
| `--blackwhite` | `-bw` | Create a black and white PDF instead of colored text |
| `--config` | | Save the PDF to the `.config` folder for use as a default with other tools |
| `--list-sizes` | `-ls` | List all available page sizes and exit |

---

## CreateMimePackage

Creates a MIME package (`.mjm`) from a JMF message, JDF ticket, and PDF file. The resulting package can be sent to PRISMAsync using `JMFSubmitter`.

```
CreateMimePackage.exe [--jmf FILE] [--jdf FILE] [--pdf URL] [--output FILE]
```

| Argument | Short | Description |
|---|---|---|
| `--jmf FILE` | `-j` | JMF message file (default: `.config\SubmitQueueEntry.jmf`) |
| `--jdf FILE` | `-t` | JDF ticket file (default: `.config\Template.jdf`) |
| `--pdf URL` | `-p` | PDF to include, as `file://` path or `http://` URL (default: `.config\Test.pdf`) |
| `--output FILE` | `-o` | Output `.mjm` file name (default: filename based on timestamp) |

---

## JMFSubmitter

Submits a job to PRISMAsync using JMF/JDF/PDF or a pre-built MIME package. Prints the returned `QueueEntryID` on success.

```
JMFSubmitter.exe [--url URL] [--jmf FILE] [--jdf FILE] [--pdf URL] [--mime FILE] [--silent] [--chunksize SIZE]
```

| Argument | Short | Description |
|---|---|---|
| `--url URL` | `-u` | PRISMAsync JMF URL (default: `http://PRISMAsync.cpp.canon:8010`) |
| `--jmf FILE` | `-j` | JMF message file (default: `.config\SubmitQueueEntry.jmf`) |
| `--jdf FILE` | `-t` | JDF ticket file (default: `.config\Template.jdf`) |
| `--pdf URL` | `-p` | PDF as `file://` path or `http://` URL. Using `file://` embeds the PDF in the MIME package |
| `--mime FILE` | `-m` | Send a pre-built MIME package directly; takes priority over all other options |
| `--silent` | `-s` | Suppress output; submit without printing the QueueEntryID |
| `--chunksize SIZE` | `-c` | Upload chunk size (e.g. `10k`, `5M`). Default `0` disables chunking |

---

## RemoveQueueEntries

Removes queue entries from PRISMAsync, filtered by status or by a specific QueueEntryID.

```
RemoveQueueEntries.exe [--url URL] [--status STATUS | --id ID]
```

| Argument | Short | Description |
|---|---|---|
| `--url URL` | `-u` | PRISMAsync JMF URL (default: `http://PRISMAsync.cpp.canon:8010`) |
| `--status STATUS` | `-s` | Remove entries with this status (e.g. `Aborted`, `Completed`, `Held`). Use `" "` to remove all. Multiple statuses: `"Aborted Completed"` |
| `--id ID` | `-i` | Remove a single entry by its QueueEntryID |

> `--status` and `--id` cannot be used together.

---

## ReceiveSignals

Starts a local web server to receive JMF signal subscriptions from PRISMAsync. Each received signal is saved as an XML file. A simple UI shows the subscription URL to use in PRISMAsync and the number of signals received.

```
ReceiveSignals.exe [--ip ADDRESS] [--port PORT] [--folder FOLDER] [--debug]
```

| Argument | Short | Description |
|---|---|---|
| `--ip ADDRESS` | | IP address to listen on (default: auto-detected) |
| `--port PORT` | | Port to listen on (default: `9090`) |
| `--folder FOLDER` | | Folder where received signals are saved (default: `_received`) |
| `--debug` | `-d` | Suppress UI output; only write signals to files |

---

## Configuration (.config folder)

Several tools look for default files in a `.config` folder located in the same directory as the tool. Run `SetupConfig` to create this folder with default content. Files can be customised afterwards:

| File | Used by | Description |
|---|---|---|
| `SubmitQueueEntry.jmf` | `CreateMimePackage`, `JMFSubmitter` | Default JMF submit message |
| `Template.jdf` | `CreateMimePackage`, `JMFSubmitter` | Default JDF print ticket |
| `Test.pdf` | `CreateMimePackage`, `JMFSubmitter` | Default test PDF |
| `QueueStatus.jmf` | Internal | JMF queue status query |
| `RemoveQueueEntry.jmf` | `RemoveQueueEntries` | JMF remove queue entry message |
