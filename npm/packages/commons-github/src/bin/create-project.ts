#!/usr/bin/env node

import {fail, printSummary, report} from '@aimarchirico/commons-project';
import {gh, ghJson, ghOrThrow, repoContext} from '../services/gh.js';

type Project = {number: number; title: string};

const nodes = (value: {nodes?: Project[]; Nodes?: Project[]}): Project[] =>
  value.nodes ?? value.Nodes ?? [];

const linkedProjects = (slug: string): Project[] => {
  const data = ghJson<{projectsV2: {nodes?: Project[]; Nodes?: Project[]}}>([
    'repo',
    'view',
    slug,
    '--json',
    'projectsV2',
  ]);
  return nodes(data.projectsV2);
};

const ownedProject = (owner: string, title: string): Project | undefined => {
  const result = gh(['project', 'list', '--owner', owner, '--format', 'json']);
  if (result.status !== 0) return undefined;
  const data = JSON.parse(result.stdout) as {projects?: Project[]};
  return (data.projects ?? []).find(project => project.title === title);
};

const link = (owner: string, slug: string, number: number): void => {
  ghOrThrow(['project', 'link', String(number), '--owner', owner, '-R', slug]);
};

const COMMONS_OWNER = 'aimarchirico';
const COMMONS_PROJECT_TITLE = 'Commons Template';

const titleCase = (value: string): string =>
  (value.match(/[A-Za-z0-9]+/g) ?? [])
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');

const {owner, repo, slug} = repoContext();
const title = titleCase(repo);

try {
  const linked = linkedProjects(slug).find(project => project.title === title);
  if (linked) {
    report(
      `project "${title}"`,
      'present',
      `#${linked.number} linked to ${slug}`,
    );
  } else {
    const existing = ownedProject(owner, title);
    if (existing) {
      link(owner, slug, existing.number);
      report(`project "${title}"`, 'updated', `#${existing.number} linked`);
    } else {
      const source = ownedProject(COMMONS_OWNER, COMMONS_PROJECT_TITLE);
      if (!source) {
        fail(
          `Could not find a project titled "${COMMONS_PROJECT_TITLE}" owned by ${COMMONS_OWNER} to copy.`,
        );
      }
      const copied = JSON.parse(
        ghOrThrow([
          'project',
          'copy',
          String(source.number),
          '--source-owner',
          COMMONS_OWNER,
          '--target-owner',
          owner,
          '--title',
          title,
          '--format',
          'json',
        ]),
      ) as {number: number};
      link(owner, slug, copied.number);
      report(
        `project "${title}"`,
        'created',
        `#${copied.number} copied from ${COMMONS_OWNER}/#${source.number}`,
      );
    }
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('create-project');
