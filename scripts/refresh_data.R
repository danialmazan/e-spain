#!/usr/bin/env Rscript

# R loads ~/.Renviron before this script starts. The Python child inherits
# ESIOS_TOKEN without the value ever being printed or written into the repo.
args <- commandArgs(trailingOnly = TRUE)
if (!nzchar(Sys.getenv("ESIOS_TOKEN"))) {
  stop("ESIOS_TOKEN is not available. Add it to ~/.Renviron or the process environment.")
}
status <- system2("python3", c("scripts/ingest_sources.py", args))
quit(status = status)
