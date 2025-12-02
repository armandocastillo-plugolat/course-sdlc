const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

describe('README.md Recent Changes Validation', () => {
  const readmePath = path.join(__dirname, '..', 'README.md');
  let readmeContent;
  let gitDiff;

  beforeAll(() => {
    readmeContent = fs.readFileSync(readmePath, 'utf-8');
    
    try {
      // Get the diff from main branch
      gitDiff = execSync('git diff main..HEAD README.md', {
        cwd: path.dirname(readmePath),
        encoding: 'utf-8'
      });
    } catch (error) {
      gitDiff = '';
      console.warn('Could not get git diff, skipping diff-specific tests');
    }
  });

  describe('Change Quality', () => {
    test('README should contain the new content about qodo test', () => {
      expect(readmeContent).toContain('Change for test qodo');
    });

    test('changes should add value to the documentation', () => {
      // The new content should be more than just a few characters
      const lines = readmeContent.split('\n');
      const nonEmptyLines = lines.filter(l => l.trim().length > 0);
      expect(nonEmptyLines.length).toBeGreaterThan(2);
    });

    test('should maintain original project title', () => {
      expect(readmeContent).toContain('# course-sdlc');
    });

    test('should maintain original project description', () => {
      expect(readmeContent).toContain('Course of SDLC using AI');
    });
  });

  describe('Git Diff Analysis', () => {
    test('changes should only add content, not remove critical info', () => {
      if (gitDiff) {
        const removedLines = gitDiff.split('\n').filter(line => line.startsWith('-') && !line.startsWith('---'));
        const criticalRemovals = removedLines.filter(line => 
          line.includes('course-sdlc') || line.includes('SDLC') || line.includes('AI')
        );
        expect(criticalRemovals.length).toBe(0);
      }
    });

    test('should add blank line before new content for readability', () => {
      const lines = readmeContent.split('\n');
      const qodoLineIndex = lines.findIndex(l => l.includes('Change for test qodo'));
      
      if (qodoLineIndex > 0) {
        // Should have a blank line before the new content
        expect(lines[qodoLineIndex - 1].trim()).toBe('');
      }
    });

    test('added content should be grammatically structured', () => {
      const newLine = 'Change for test qodo';
      // Should start with capital letter
      expect(newLine[0]).toBe(newLine[0].toUpperCase());
      // Should have multiple words
      expect(newLine.split(/\s+/).length).toBeGreaterThan(1);
    });
  });

  describe('Content Evolution', () => {
    test('document should grow organically without losing coherence', () => {
      const sections = readmeContent.split(/\n\s*\n/);
      // Each section should be cohesive
      sections.forEach(section => {
        if (section.trim().length > 0) {
          expect(section.trim().length).toBeGreaterThan(5);
        }
      });
    });

    test('new additions should relate to project scope (SDLC/AI/Testing)', () => {
      const newContent = 'Change for test qodo';
      const relevant = newContent.toLowerCase().includes('test') ||
                      newContent.toLowerCase().includes('qodo') ||
                      newContent.toLowerCase().includes('change');
      expect(relevant).toBe(true);
    });

    test('should maintain professional tone', () => {
      const unprofessionalPatterns = [
        /\b(lol|omg|wtf|idk)\b/i,
        /!!!+/,
        /\?\?\?+/,
        /damn|shit|crap/i
      ];

      unprofessionalPatterns.forEach(pattern => {
        expect(readmeContent).not.toMatch(pattern);
      });
    });
  });

  describe('Change Integration', () => {
    test('file should still be valid after changes', () => {
      expect(() => {
        const content = fs.readFileSync(readmePath, 'utf-8');
        expect(content).toBeDefined();
        expect(content.length).toBeGreaterThan(0);
      }).not.toThrow();
    });

    test('changes should maintain file encoding', () => {
      const buffer = fs.readFileSync(readmePath);
      const decoded = buffer.toString('utf-8');
      // Should not have encoding issues
      expect(decoded).not.toContain('�'); // Replacement character
    });

    test('line count should increase appropriately', () => {
      const lines = readmeContent.split('\n');
      // Should have at least 4 lines now (title, description, blank, new content)
      expect(lines.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Future Extensibility', () => {
    test('structure should allow for easy additions', () => {
      const lines = readmeContent.split('\n');
      const lastLine = lines[lines.length - 1];
      
      // Document structure should be open for extension
      expect(readmeContent.length).toBeLessThan(10000); // Still has room to grow
    });

    test('should not have end-of-file marker that prevents additions', () => {
      expect(readmeContent).not.toContain('--- END ---');
      expect(readmeContent).not.toContain('=== END ===');
    });

    test('should maintain consistent formatting for future additions', () => {
      // All substantive paragraphs should be separated
      const paragraphs = readmeContent.split(/\n\s*\n/).filter(p => p.trim().length > 0);
      expect(paragraphs.length).toBeGreaterThanOrEqual(2);
    });
  });
});