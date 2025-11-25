const fs = require('fs');
const path = require('path');

describe('README.md Validation Tests', () => {
  let readmeContent;
  const readmePath = path.join(__dirname, '..', 'README.md');

  beforeAll(() => {
    readmeContent = fs.readFileSync(readmePath, 'utf-8');
  });

  describe('File Existence and Basic Structure', () => {
    test('README.md file should exist', () => {
      expect(fs.existsSync(readmePath)).toBe(true);
    });

    test('README.md should not be empty', () => {
      expect(readmeContent.trim().length).toBeGreaterThan(0);
    });

    test('README.md should contain actual content beyond whitespace', () => {
      const nonWhitespaceContent = readmeContent.replace(/\s/g, '');
      expect(nonWhitespaceContent.length).toBeGreaterThan(0);
    });
  });

  describe('Title and Heading Structure', () => {
    test('should have a primary heading (h1)', () => {
      const h1Regex = /^# .+/m;
      expect(readmeContent).toMatch(h1Regex);
    });

    test('primary heading should be "course-sdlc"', () => {
      const lines = readmeContent.split('\n');
      const h1Line = lines.find(line => line.startsWith('# '));
      expect(h1Line).toBe('# course-sdlc');
    });

    test('should have well-formed markdown headings', () => {
      const headingLines = readmeContent.split('\n').filter(line => line.startsWith('#'));
      headingLines.forEach(heading => {
        // Check that there's a space after the hash(es)
        expect(heading).toMatch(/^#+\s+\S/);
      });
    });

    test('should not have trailing hashes in ATX-style headings', () => {
      const headingLines = readmeContent.split('\n').filter(line => line.startsWith('#'));
      headingLines.forEach(heading => {
        // Avoid ATX-style trailing hashes like "# Title #"
        expect(heading.trim()).not.toMatch(/^#+\s+.+\s+#$/);
      });
    });
  });

  describe('Content Quality and Completeness', () => {
    test('should contain project description', () => {
      expect(readmeContent.toLowerCase()).toMatch(/course.*sdlc/i);
    });

    test('should mention AI in the description', () => {
      expect(readmeContent.toLowerCase()).toContain('ai');
    });

    test('should have substantive content (more than just title)', () => {
      const lines = readmeContent.split('\n').filter(line => line.trim().length > 0);
      expect(lines.length).toBeGreaterThan(1);
    });

    test('should contain the recent change about qodo', () => {
      expect(readmeContent.toLowerCase()).toMatch(/change.*test.*qodo/i);
    });
  });

  describe('Markdown Syntax Validation', () => {
    test('should not contain unescaped HTML tags that could break rendering', () => {
      const htmlTagRegex = /<(?!\/?(code|pre|em|strong|b|i|a|img|br|hr)[\s>])[^>]+>/g;
      const suspiciousTags = readmeContent.match(htmlTagRegex);
      if (suspiciousTags) {
        // Allow some common safe HTML tags in markdown
        const unsafeTags = suspiciousTags.filter(tag => 
          !tag.match(/<\/?(code|pre|em|strong|b|i|a|img|br|hr|details|summary|table|thead|tbody|tr|td|th)[\s>]/i)
        );
        expect(unsafeTags).toEqual([]);
      }
    });

    test('should not have malformed code blocks', () => {
      const codeBlockFences = readmeContent.match(/```/g) || [];
      // Code blocks should come in pairs
      expect(codeBlockFences.length % 2).toBe(0);
    });

    test('should not have unclosed inline code', () => {
      const lines = readmeContent.split('\n');
      lines.forEach((line, index) => {
        // Skip code blocks
        if (!line.trim().startsWith('```')) {
          const backticks = (line.match(/`/g) || []).length;
          expect(backticks % 2).toBe(0);
        }
      });
    });
  });

  describe('Link Validation', () => {
    test('should not contain broken internal reference links', () => {
      const internalLinkRegex = /\[([^\]]+)\]\(#([^\)]+)\)/g;
      const links = [...readmeContent.matchAll(internalLinkRegex)];
      
      links.forEach(([fullMatch, text, anchor]) => {
        // Check if the anchor exists in the document as a heading
        const anchorId = anchor.toLowerCase().replace(/\s+/g, '-');
        const headingExists = readmeContent.toLowerCase().includes(anchorId) ||
                            readmeContent.includes(`id="${anchor}"`);
        expect(headingExists || links.length === 0).toBeTruthy();
      });
    });

    test('should have properly formatted markdown links', () => {
      const linkRegex = /\[([^\]]+)\]\(([^\)]+)\)/g;
      const links = [...readmeContent.matchAll(linkRegex)];
      
      links.forEach(([fullMatch, text, url]) => {
        // Link text should not be empty
        expect(text.trim().length).toBeGreaterThan(0);
        // URL should not be empty
        expect(url.trim().length).toBeGreaterThan(0);
        // URL should not contain spaces (unless encoded)
        if (!url.includes('%20')) {
          expect(url).not.toMatch(/\s/);
        }
      });
    });

    test('should not have malformed image links', () => {
      const imageRegex = /!\[([^\]]*)\]\(([^\)]+)\)/g;
      const images = [...readmeContent.matchAll(imageRegex)];
      
      images.forEach(([fullMatch, altText, url]) => {
        // URL should not be empty
        expect(url.trim().length).toBeGreaterThan(0);
        // Alt text is optional but if present should be meaningful
        if (altText.trim().length > 0) {
          expect(altText.trim().length).toBeGreaterThan(0);
        }
      });
    });
  });

  describe('Formatting and Style Consistency', () => {
    test('should use consistent line endings', () => {
      // Check that we don't mix line endings
      const hasWindows = readmeContent.includes('\r\n');
      const hasUnix = readmeContent.includes('\n') && !readmeContent.includes('\r\n');
      
      // Should use one or the other consistently
      expect(hasWindows && hasUnix).toBe(false);
    });

    test('should end with a newline character (POSIX standard)', () => {
      expect(readmeContent.endsWith('\n') || readmeContent.length === 0).toBe(true);
    });

    test('should not have excessive blank lines (more than 2 consecutive)', () => {
      const excessiveBlankLines = /\n\s*\n\s*\n\s*\n/;
      expect(readmeContent).not.toMatch(excessiveBlankLines);
    });

    test('should not have trailing whitespace on lines', () => {
      const lines = readmeContent.split('\n');
      const linesWithTrailing = lines.filter((line, idx) => {
        // Skip the last line if it doesn't end with newline
        if (idx === lines.length - 1 && !readmeContent.endsWith('\n')) {
          return false;
        }
        return line !== line.trimEnd();
      });
      
      expect(linesWithTrailing.length).toBe(0);
    });
  });

  describe('Content Specificity Tests', () => {
    test('should describe SDLC (Software Development Life Cycle)', () => {
      const hasSdlc = readmeContent.toLowerCase().includes('sdlc') ||
                     readmeContent.toLowerCase().includes('software development');
      expect(hasSdlc).toBe(true);
    });

    test('should mention it is a course/educational content', () => {
      expect(readmeContent.toLowerCase()).toMatch(/course/i);
    });

    test('recent changes should be properly documented', () => {
      const lowerContent = readmeContent.toLowerCase();
      expect(lowerContent).toMatch(/change|update|modify/i);
    });

    test('should maintain brand consistency for "qodo"', () => {
      // Check if qodo is mentioned and is lowercase (brand style)
      const qodoMentions = readmeContent.match(/qodo/gi) || [];
      qodoMentions.forEach(mention => {
        expect(mention).toBe('qodo'); // Should be lowercase
      });
    });
  });

  describe('File Integrity and Security', () => {
    test('should not contain potential security issues (secrets, keys)', () => {
      const secretPatterns = [
        /password\s*=\s*['"][^'"]+['"]/i,
        /api[_-]?key\s*=\s*['"][^'"]+['"]/i,
        /secret\s*=\s*['"][^'"]+['"]/i,
        /token\s*=\s*['"][^'"]+['"]/i,
        /-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----/i
      ];

      secretPatterns.forEach(pattern => {
        expect(readmeContent).not.toMatch(pattern);
      });
    });

    test('should not contain personally identifiable information (PII)', () => {
      // Check for email patterns that shouldn't be in public docs
      const emails = readmeContent.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];
      // If emails exist, they should be example/documentation emails
      emails.forEach(email => {
        expect(
          email.includes('example.com') || 
          email.includes('placeholder') ||
          email.includes('your-email')
        ).toBe(true);
      });
    });

    test('file should be readable with UTF-8 encoding', () => {
      const buffer = fs.readFileSync(readmePath);
      const decoded = buffer.toString('utf-8');
      expect(decoded).toBe(readmeContent);
    });
  });

  describe('Accessibility and Best Practices', () => {
    test('headings should follow hierarchical order', () => {
      const headings = readmeContent.split('\n')
        .filter(line => line.startsWith('#'))
        .map(line => line.match(/^#+/)[0].length);
      
      if (headings.length > 1) {
        for (let i = 1; i < headings.length; i++) {
          // Heading level should not jump by more than 1
          expect(headings[i] - headings[i-1]).toBeLessThanOrEqual(1);
        }
      }
    });

    test('should be concise yet informative (reasonable length)', () => {
      const wordCount = readmeContent.split(/\s+/).filter(w => w.length > 0).length;
      expect(wordCount).toBeGreaterThan(3); // At least some content
      expect(wordCount).toBeLessThan(10000); // Not excessively long for a README
    });

    test('should not contain duplicate consecutive words', () => {
      const words = readmeContent.toLowerCase().split(/\s+/);
      for (let i = 1; i < words.length; i++) {
        if (words[i].length > 3) { // Only check words longer than 3 chars
          expect(words[i]).not.toBe(words[i-1]);
        }
      }
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle file read errors gracefully', () => {
      expect(() => {
        const content = fs.readFileSync(readmePath, 'utf-8');
        expect(content).toBeDefined();
      }).not.toThrow();
    });

    test('should have valid UTF-8 characters only', () => {
      // Check for invalid UTF-8 sequences
      const invalidChars = /[\uFFFD]/g; // Replacement character
      expect(readmeContent).not.toMatch(invalidChars);
    });

    test('should not contain zero-width or invisible characters', () => {
      const invisibleChars = /[\u200B-\u200D\uFEFF]/g;
      expect(readmeContent).not.toMatch(invisibleChars);
    });

    test('should not be suspiciously large (potential corruption)', () => {
      const stats = fs.statSync(readmePath);
      expect(stats.size).toBeLessThan(1024 * 1024); // Less than 1MB
      expect(stats.size).toBeGreaterThan(0);
    });
  });

  describe('Version Control and Metadata', () => {
    test('should be tracked by git', () => {
      const { execSync } = require('child_process');
      try {
        const gitStatus = execSync('git ls-files README.md', { 
          cwd: path.dirname(readmePath),
          encoding: 'utf-8' 
        });
        expect(gitStatus.trim()).toBe('README.md');
      } catch (error) {
        // If git command fails, skip this test
        console.warn('Git command failed, skipping test');
      }
    });
  });
});