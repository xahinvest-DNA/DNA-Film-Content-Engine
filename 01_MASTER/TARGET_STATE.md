# Target State

Last updated: 2026-04-11
Status: active

## Product definition

DNA Film Content Engine is desktop-first software for creating content from film analysis.

Its core job is to transform meaning structure into usable content outputs.

## MVP path

The MVP product must support one honest end-to-end workflow:

`analysis text -> semantic map -> matching -> scene/timecode chain -> rough cut -> output builder -> export package`

## What the user must be able to do

The user must be able to:

- create a project;
- load analysis text;
- generate and edit the semantic map;
- connect semantic units to film-side sources;
- choose accepted references;
- fix a scene/timecode chain;
- assemble a rough-cut set;
- run at least one real output builder;
- receive an exportable content artifact inside the project package.

## Success definition

The product is successful when one real project can be taken from analysis input to a usable content artifact without rebuilding the workflow manually outside the software.

## What does not count as success

The project is not considered done because it has:

- more gates;
- more stubs;
- more cues;
- more internal workflow layers.

Those only matter if they help produce the final content artifact.

## MVP output rule

At least one builder must produce a real artifact that is:

- stored in the project package;
- readable by the user in the UI;
- export-ready enough to be used as a content-production result.
