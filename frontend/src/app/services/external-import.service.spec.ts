import { TestBed } from '@angular/core/testing';

import { ExternalImportService } from './external-import.service';

describe('ExternalImportService', () => {
  let service: ExternalImportService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ExternalImportService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
