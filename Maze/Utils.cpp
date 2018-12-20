
#include "Utils.h"

#include <stdio.h>
#include <stdlib.h>

#ifdef __unix
#define fopen_s(pFile,filename,mode) ((*(pFile))=fopen((filename),  (mode)))==NULL
#endif

unsigned char* createBitmapFileHeader(int height, int width) {
  int fileSize = fileHeaderSize + infoHeaderSize + bytesPerPixel * height * width;

  static unsigned char fileHeader[] = {
    0,0, /// signature
    0,0,0,0, /// image file size in bytes
    0,0,0,0, /// reserved
    0,0,0,0, /// start of pixel array
  };

  fileHeader[0] = (unsigned char)('B');
  fileHeader[1] = (unsigned char)('M');
  fileHeader[2] = (unsigned char)(fileSize);
  fileHeader[3] = (unsigned char)(fileSize >> 8);
  fileHeader[4] = (unsigned char)(fileSize >> 16);
  fileHeader[5] = (unsigned char)(fileSize >> 24);
  fileHeader[10] = (unsigned char)(fileHeaderSize + infoHeaderSize);

  return fileHeader;
}

unsigned char* createBitmapInfoHeader(int height, int width) {
  static unsigned char infoHeader[] = {
    0,0,0,0, /// header size
    0,0,0,0, /// image width
    0,0,0,0, /// image height
    0,0, /// number of color planes
    0,0, /// bits per pixel
    0,0,0,0, /// compression
    0,0,0,0, /// image size
    0,0,0,0, /// horizontal resolution
    0,0,0,0, /// vertical resolution
    0,0,0,0, /// colors in color table
    0,0,0,0, /// important color count
  };

  infoHeader[0] = (unsigned char)(infoHeaderSize);
  infoHeader[4] = (unsigned char)(width);
  infoHeader[5] = (unsigned char)(width >> 8);
  infoHeader[6] = (unsigned char)(width >> 16);
  infoHeader[7] = (unsigned char)(width >> 24);
  infoHeader[8] = (unsigned char)(height);
  infoHeader[9] = (unsigned char)(height >> 8);
  infoHeader[10] = (unsigned char)(height >> 16);
  infoHeader[11] = (unsigned char)(height >> 24);
  infoHeader[12] = (unsigned char)(1);
  infoHeader[14] = (unsigned char)(bytesPerPixel * 8);

  return infoHeader;
}

void generateBitmapImage(const std::vector< std::vector<bool> >& image,
                         int height, int width, const char* imageFileName)
{
  unsigned char* fileHeader = createBitmapFileHeader(height, width);
  unsigned char* infoHeader = createBitmapInfoHeader(height, width);
  unsigned char padding[3] = { 0, 0, 0 };
  int paddingSize = (4 - (width * bytesPerPixel) % 4) % 4;

  FILE* imageFile = nullptr;
  fopen_s(&imageFile, imageFileName, "wb");

  fwrite(fileHeader, 1, fileHeaderSize, imageFile);
  fwrite(infoHeader, 1, infoHeaderSize, imageFile);

  const unsigned char white[] = { 255, 255, 255 };
  const unsigned char black[] = { 12, 12, 12 };

  for (int h = 0; h < height; ++h) {
    for (int w = 0; w < width; ++w) {
      if (image[w][h]) {
        fwrite(black, 1, 3, imageFile);
      } else {
        fwrite(white, 1, 3, imageFile);
      }
      fwrite(padding, 1, paddingSize, imageFile);
    }
  }

  fclose(imageFile);
}

void generateBitmapImage(const std::vector< std::vector<char> >& image,
                         int height, int width, const char* imageFileName)
{
  unsigned char* fileHeader = createBitmapFileHeader(height, width);
  unsigned char* infoHeader = createBitmapInfoHeader(height, width);
  unsigned char padding[3] = { 0, 0, 0 };
  int paddingSize = (4 - (width*bytesPerPixel) % 4) % 4;

  FILE* imageFile = nullptr;
  fopen_s(&imageFile, imageFileName, "wb");

  fwrite(fileHeader, 1, fileHeaderSize, imageFile);
  fwrite(infoHeader, 1, infoHeaderSize, imageFile);

  unsigned char clr[] = { 64, 64, 64 };

  for (int h = 0; h < height; ++h) {
    for (int w = 0; w < width; ++w) {
      const unsigned char v = image[w][h];
      clr[0] = v;
      clr[1] = v;
      clr[2] = v;
      fwrite(clr, 1, 3, imageFile);
      fwrite(padding, 1, paddingSize, imageFile);
    }
  }

  fclose(imageFile);
}
