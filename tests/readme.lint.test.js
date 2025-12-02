const fs = require('fs');
const path = require('path');

describe('README.md Markdown Linting (Integration)', () => {
  const readmePath = path.join(__dirname, '..', 'README.md');
  let readmeContent;

  beforeAll(() => {
    readmeContent = fs.readFileSync(readmePath, 'utf-8');
  });

  describe('Markdown Best Practices', () => {
    test('should not have bare URLs (should be in link format)', () => {
      // Match URLs not already in markdown link format
      const lines = readmeContent.split('\n');
      lines.forEach(line => {
        // Skip if line contains markdown link
        if (!line.includes('](') && !line.startsWith('```')) {
          const bareUrlRegex = /(?<!\()(https?:\/\/[^\s)]+)(?!\))/g;
          const matches = line.match(bareUrlRegex);
          if (matches) {
            matches.forEach(url => {
              // Bare URLs should be wrapped in <>  or proper links
              expect(line).toMatch(new RegExp(`<${url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}>`));
            });
          }
        }
      });
    });

    test('should use emphasis correctly (not mixing styles)', () => {
      // Check for mixing * and _ for emphasis
      const emphasisBlocks = readmeContent.match(/(\*|_)[^*_\n]+\1/g) || [];
      const asteriskEmphasis = emphasisBlocks.filter(b => b.startsWith('*'));
      const underscoreEmphasis = emphasisBlocks.filter(b => b.startsWith('_'));
      
      // Prefer consistent style throughout document
      if (asteriskEmphasis.length > 0 && underscoreEmphasis.length > 0) {
        // Mixed emphasis is allowed, but check for consistency within paragraphs
        const paragraphs = readmeContent.split(/\n\s*\n/);
        paragraphs.forEach(para => {
          const paraAsterisk = (para.match(/\*[^*\n]+\*/g) || []).length;
          const paraUnderscore = (para.match(/_[^_\n]+_/g) || []).length;
          // Within a paragraph, should be consistent
          expect(paraAsterisk === 0 || paraUnderscore === 0).toBe(true);
        });
      }
    });

    test('should have proper list formatting', () => {
      const lines = readmeContent.split('\n');
      const listItems = lines.filter(line => /^\s*[-*+]\s/.test(line));
      
      listItems.forEach(item => {
        // List items should have space after marker
        expect(item).toMatch(/^\s*[-*+]\s+\S/);
      });
    });

    test('should have proper ordered list formatting', () => {
      const lines = readmeContent.split('\n');
      const orderedItems = lines.filter(line => /^\s*\d+\.\s/.test(line));
      
      orderedItems.forEach(item => {
        // Ordered list items should have space after number and period
        expect(item).toMatch(/^\s*\d+\.\s+\S/);
      });
    });

    test('should not have multiple blank lines between content', () => {
      const tripleNewline = /\n\n\n+/g;
      const matches = readmeContent.match(tripleNewline);
      expect(matches).toBeNull();
    });
  });

  describe('Common Markdown Mistakes', () => {
    test('should not have unmatched brackets in links', () => {
      const lines = readmeContent.split('\n');
      lines.forEach(line => {
        const openBrackets = (line.match(/\[/g) || []).length;
        const closeBrackets = (line.match(/\]/g) || []).length;
        const openParens = (line.match(/\(/g) || []).length;
        const closeParens = (line.match(/\)/g) || []).length;
        
        // In markdown links, brackets and parens should balance
        // But only check if it looks like it's trying to be a link
        if (line.includes('[') || line.includes(']')) {
          expect(openBrackets).toBe(closeBrackets);
        }
      });
    });

    test('should not have misplaced emphasis markers', () => {
      // Check for emphasis markers with improper spacing
      const badEmphasis = /\w\*\w|\w_\w/g;
      expect(readmeContent).not.toMatch(badEmphasis);
    });

    test('should not have hash symbols without proper heading format', () => {
      const lines = readmeContent.split('\n');
      lines.forEach(line => {
        if (line.includes('#') && !line.startsWith('#')) {
          // If # appears mid-line, it should be in a code block or escaped
          const inCodeBlock = line.includes('`#') || line.includes('```');
          const escaped = line.includes('\\#');
          expect(inCodeBlock || escaped || !line.match(/[^`]#(?!#)/) ).toBe(true);
        }
      });
    });
  });

  describe('GitHub Flavored Markdown Features', () => {
    test('task lists should be properly formatted if present', () => {
      const taskListRegex = /^\s*[-*]\s+\[([ xX])\]\s+/gm;
      const taskLists = readmeContent.match(taskListRegex) || [];
      
      taskLists.forEach(task => {
        // Should have proper format: - [ ] or - [x]
        expect(task).toMatch(/^\s*[-*]\s+\[([ xX])\]\s+/);
      });
    });

    test('should not have broken table syntax if tables are present', () => {
      const tableLines = readmeContent.split('\n').filter(line => line.includes('|'));
      
      if (tableLines.length > 0) {
        // If there are pipes, check for table header separator
        const hasSeparator = tableLines.some(line => /^\|?\s*[-:]+\s*\|/.test(line));
        if (tableLines.length > 2) {
          expect(hasSeparator).toBe(true);
        }
      }
    });

    test('code blocks should specify language where applicable', () => {
      const codeBlocks = readmeContent.match(/```(\w*)\n/g) || [];
      
      codeBlocks.forEach((block, idx) => {
        const language = block.match(/```(\w*)/)[1];
        // If code block is long (more than 10 lines), should have language
        const blockContent = readmeContent.split('```')[idx * 2 + 1] || '';
        if (blockContent.split('\n').length > 10) {
          expect(language.length).toBeGreaterThan(0);
        }
      });
    });
  });

  describe('Documentation Completeness', () => {
    test('should provide adequate context for the project', () => {
      // A good README should have more than just a title
      const substantiveLines = readmeContent
        .split('\n')
        .filter(line => line.trim().length > 0 && !line.startsWith('#'))
        .filter(line => line.trim().length > 10); // Meaningful content
      
      expect(substantiveLines.length).toBeGreaterThan(0);
    });

    test('should not have placeholder text left from templates', () => {
      const placeholders = [
        /\[your[- ]?name\]/i,
        /\[project[- ]?name\]/i,
        /\[description\]/i,
        /TODO:/,
        /FIXME:/,
        /xxx/i
      ];

      placeholders.forEach(pattern => {
        expect(readmeContent).not.toMatch(pattern);
      });
    });
  });
});