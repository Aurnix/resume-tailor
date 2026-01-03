#!/usr/bin/env node
/**
 * DOCX Generator for Resume Tailor
 * 
 * Reads JSON from stdin, generates ATS-friendly .docx resume
 * 
 * Usage: echo '{"content": {...}, "output_path": "resume.docx"}' | node docx_generator.js
 */

const fs = require('fs');
const { 
    Document, 
    Packer, 
    Paragraph, 
    TextRun, 
    HeadingLevel,
    AlignmentType,
    TabStopType,
    TabStopPosition,
    ExternalHyperlink,
    LevelFormat
} = require('docx');

// Read JSON from stdin
let inputData = '';
process.stdin.setEncoding('utf8');

process.stdin.on('readable', () => {
    let chunk;
    while ((chunk = process.stdin.read()) !== null) {
        inputData += chunk;
    }
});

process.stdin.on('end', async () => {
    try {
        const data = JSON.parse(inputData);
        await generateResume(data);
        console.log('Resume generated successfully');
    } catch (error) {
        console.error('Error generating resume:', error.message);
        process.exit(1);
    }
});

async function generateResume(data) {
    const { content, output_path, contact } = data;
    
    // Build document sections
    const children = [];
    
    // Header with contact info
    children.push(...createHeader(contact));
    
    // Summary
    if (content.summary) {
        children.push(...createSummary(content.summary));
    }
    
    // Experience
    if (content.roles && content.roles.length > 0) {
        children.push(...createExperience(content.roles));
    }
    
    // Skills
    if (content.skills_section && content.skills_section.length > 0) {
        children.push(...createSkills(content.skills_section));
    }
    
    // Create document
    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: {
                        font: "Arial",
                        size: 22  // 11pt
                    }
                }
            },
            paragraphStyles: [
                {
                    id: "Name",
                    name: "Name",
                    basedOn: "Normal",
                    run: { size: 36, bold: true },  // 18pt
                    paragraph: { spacing: { after: 40 } }
                },
                {
                    id: "ContactInfo",
                    name: "Contact Info",
                    basedOn: "Normal",
                    run: { size: 20 },  // 10pt
                    paragraph: { spacing: { after: 120 } }
                },
                {
                    id: "SectionHeading",
                    name: "Section Heading",
                    basedOn: "Normal",
                    run: { size: 24, bold: true, allCaps: true },  // 12pt
                    paragraph: { 
                        spacing: { before: 240, after: 120 },
                        border: { bottom: { style: "single", size: 6, color: "000000" } }
                    }
                },
                {
                    id: "JobTitle",
                    name: "Job Title",
                    basedOn: "Normal",
                    run: { size: 22, bold: true },  // 11pt
                    paragraph: { spacing: { before: 120, after: 40 } }
                },
                {
                    id: "CompanyLine",
                    name: "Company Line",
                    basedOn: "Normal",
                    run: { size: 22 },  // 11pt
                    paragraph: { spacing: { after: 80 } }
                },
                {
                    id: "BulletPoint",
                    name: "Bullet Point",
                    basedOn: "Normal",
                    run: { size: 22 },  // 11pt
                    paragraph: { 
                        spacing: { after: 40 },
                        indent: { left: 360, hanging: 180 }
                    }
                }
            ]
        },
        numbering: {
            config: [
                {
                    reference: "resume-bullets",
                    levels: [{
                        level: 0,
                        format: LevelFormat.BULLET,
                        text: "•",
                        alignment: AlignmentType.LEFT,
                        style: {
                            paragraph: {
                                indent: { left: 720, hanging: 360 }
                            }
                        }
                    }]
                }
            ]
        },
        sections: [{
            properties: {
                page: {
                    margin: {
                        top: 720,    // 0.5 inch
                        right: 720,
                        bottom: 720,
                        left: 720
                    }
                }
            },
            children: children
        }]
    });
    
    // Write to file
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(output_path, buffer);
}

function createHeader(contact) {
    const elements = [];
    
    // Name
    elements.push(new Paragraph({
        style: "Name",
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: contact.name || "Your Name" })]
    }));
    
    // Contact line
    const contactParts = [];
    if (contact.location) contactParts.push(contact.location);
    if (contact.phone) contactParts.push(contact.phone);
    if (contact.email) contactParts.push(contact.email);
    if (contact.linkedin) contactParts.push(contact.linkedin);
    
    if (contactParts.length > 0) {
        elements.push(new Paragraph({
            style: "ContactInfo",
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: contactParts.join(" | ") })]
        }));
    }
    
    return elements;
}

function createSummary(summaryText) {
    return [
        new Paragraph({
            style: "SectionHeading",
            children: [new TextRun({ text: "PROFESSIONAL SUMMARY" })]
        }),
        new Paragraph({
            children: [new TextRun({ text: summaryText })]
        })
    ];
}

function createExperience(roles) {
    const elements = [];
    
    elements.push(new Paragraph({
        style: "SectionHeading",
        children: [new TextRun({ text: "PROFESSIONAL EXPERIENCE" })]
    }));
    
    for (const role of roles) {
        // Job title
        elements.push(new Paragraph({
            style: "JobTitle",
            children: [new TextRun({ text: role.title })]
        }));
        
        // Company and dates
        const dateRange = role.end_date 
            ? `${role.start_date} - ${role.end_date}`
            : `${role.start_date} - Present`;
        
        elements.push(new Paragraph({
            style: "CompanyLine",
            tabStops: [{
                type: TabStopType.RIGHT,
                position: TabStopPosition.MAX
            }],
            children: [
                new TextRun({ text: role.company, italics: true }),
                new TextRun({ text: "\t" }),
                new TextRun({ text: dateRange })
            ]
        }));
        
        // Bullets
        for (const bullet of role.bullets || []) {
            const bulletText = typeof bullet === 'string' ? bullet : bullet.text;
            elements.push(new Paragraph({
                numbering: { reference: "resume-bullets", level: 0 },
                children: [new TextRun({ text: bulletText })]
            }));
        }
    }
    
    return elements;
}

function createSkills(skills) {
    return [
        new Paragraph({
            style: "SectionHeading",
            children: [new TextRun({ text: "TECHNICAL SKILLS" })]
        }),
        new Paragraph({
            children: [new TextRun({ text: skills.join(" • ") })]
        })
    ];
}
